---
name: ruby-on-rails
description: Ruby on Rails development covering MVC architecture, Active Record models, migrations, associations, validations, controllers, routing, Action Mailer, Active Job, Hotwire/Turbo, Stimulus, testing with RSpec, and production deployment.
---

# Ruby on Rails

This skill should be used when building web applications with Ruby on Rails. It covers models, migrations, controllers, routing, Hotwire, background jobs, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build full-stack web applications with Rails
- Design database schemas with Active Record
- Implement real-time features with Hotwire/Turbo
- Set up background job processing
- Test Rails applications with RSpec

## Model with Associations

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_password
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :email, presence: true, uniqueness: { case_sensitive: false },
                    format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :username, presence: true, uniqueness: true,
                       length: { minimum: 3, maximum: 30 }

  normalizes :email, with: ->(email) { email.strip.downcase }

  scope :active, -> { where(active: true) }
  scope :recent, -> { order(created_at: :desc) }
end

# app/models/post.rb
class Post < ApplicationRecord
  belongs_to :author, class_name: "User", foreign_key: "user_id"
  has_many :comments, dependent: :destroy
  has_many :taggings, dependent: :destroy
  has_many :tags, through: :taggings

  validates :title, presence: true, length: { maximum: 200 }
  validates :body, presence: true

  scope :published, -> { where(published: true) }
  scope :draft, -> { where(published: false) }

  broadcasts_to ->(post) { "posts" }
end
```

## Migration

```ruby
# db/migrate/20240101000000_create_posts.rb
class CreatePosts < ActiveRecord::Migration[7.1]
  def change
    create_table :posts do |t|
      t.string :title, null: false
      t.text :body, null: false
      t.boolean :published, default: false, null: false
      t.references :user, null: false, foreign_key: true
      t.timestamps
    end

    add_index :posts, [:user_id, :published]
    add_index :posts, :created_at
  end
end
```

## Controller

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  before_action :authenticate_user!, except: [:index, :show]
  before_action :set_post, only: [:show, :edit, :update, :destroy]
  before_action :authorize_post!, only: [:edit, :update, :destroy]

  def index
    @posts = Post.published.includes(:author).recent.page(params[:page])
  end

  def show; end

  def create
    @post = current_user.posts.build(post_params)
    if @post.save
      redirect_to @post, notice: "Post created."
    else
      render :new, status: :unprocessable_entity
    end
  end

  def update
    if @post.update(post_params)
      redirect_to @post, notice: "Post updated."
    else
      render :edit, status: :unprocessable_entity
    end
  end

  def destroy
    @post.destroy
    redirect_to posts_url, notice: "Post deleted."
  end

  private

  def set_post
    @post = Post.find(params[:id])
  end

  def post_params
    params.require(:post).permit(:title, :body, :published, tag_ids: [])
  end

  def authorize_post!
    redirect_to posts_url unless @post.user_id == current_user.id
  end
end
```

## API Controller

```ruby
# app/controllers/api/v1/posts_controller.rb
module Api
  module V1
    class PostsController < ApplicationController
      skip_before_action :verify_authenticity_token
      before_action :authenticate_api_token!

      def index
        posts = Post.published.includes(:author).page(params[:page]).per(20)
        render json: {
          data: posts.map { |p| serialize_post(p) },
          meta: { total: posts.total_count, page: posts.current_page }
        }
      end

      def create
        post = current_user.posts.build(post_params)
        if post.save
          render json: { data: serialize_post(post) }, status: :created
        else
          render json: { errors: post.errors.full_messages }, status: :unprocessable_entity
        end
      end

      private

      def authenticate_api_token!
        token = request.headers["Authorization"]&.remove("Bearer ")
        @current_user = User.find_by(api_token: token)
        render json: { error: "Unauthorized" }, status: :unauthorized unless @current_user
      end

      def serialize_post(post)
        { id: post.id, title: post.title, author: post.author.username, created_at: post.created_at }
      end
    end
  end
end
```

## Routes

```ruby
# config/routes.rb
Rails.application.routes.draw do
  root "pages#home"

  resources :posts do
    resources :comments, only: [:create, :destroy]
  end

  namespace :api do
    namespace :v1 do
      resources :posts, only: [:index, :show, :create, :update, :destroy]
    end
  end

  get "up" => "rails/health#show", as: :rails_health_check
end
```

## Hotwire / Turbo

```erb
<!-- app/views/posts/index.html.erb -->
<%= turbo_stream_from "posts" %>

<div id="posts">
  <%= render @posts %>
</div>

<!-- app/views/posts/_post.html.erb -->
<%= turbo_frame_tag post do %>
  <article id="<%= dom_id(post) %>">
    <h2><%= link_to post.title, post %></h2>
    <p>By <%= post.author.username %></p>
  </article>
<% end %>
```

## Background Jobs

```ruby
# app/jobs/send_newsletter_job.rb
class SendNewsletterJob < ApplicationJob
  queue_as :default
  retry_on Net::OpenTimeout, wait: :polynomially_longer, attempts: 5

  def perform(user_id)
    user = User.find(user_id)
    NewsletterMailer.weekly_digest(user).deliver_now
  end
end

# Enqueue
SendNewsletterJob.perform_later(user.id)
SendNewsletterJob.set(wait: 1.hour).perform_later(user.id)
```

## RSpec Testing

```ruby
# spec/models/post_spec.rb
RSpec.describe Post, type: :model do
  describe "validations" do
    it { is_expected.to validate_presence_of(:title) }
    it { is_expected.to validate_presence_of(:body) }
    it { is_expected.to belong_to(:author).class_name("User") }
  end

  describe ".published" do
    it "returns only published posts" do
      published = create(:post, published: true)
      create(:post, published: false)
      expect(Post.published).to eq([published])
    end
  end
end

# spec/requests/posts_spec.rb
RSpec.describe "Posts", type: :request do
  describe "GET /posts" do
    it "returns success" do
      get posts_path
      expect(response).to have_http_status(:success)
    end
  end

  describe "POST /posts" do
    let(:user) { create(:user) }

    it "creates a post" do
      sign_in user
      expect {
        post posts_path, params: { post: { title: "New", body: "Content" } }
      }.to change(Post, :count).by(1)
    end
  end
end
```

## CLI Commands

```bash
rails new myapp --database=postgresql
rails generate model Post title:string body:text user:references
rails generate controller Posts index show new create edit update destroy
rails db:migrate
rails server
rails console
rails routes
```

## Additional Resources

- Rails Guides: https://guides.rubyonrails.org/
- Hotwire: https://hotwired.dev/
- RSpec Rails: https://rspec.info/
