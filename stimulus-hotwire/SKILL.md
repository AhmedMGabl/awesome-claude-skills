---
name: stimulus-hotwire
description: Stimulus and Hotwire patterns covering controllers, targets, values, actions, outlets, Turbo Drive, Turbo Frames, Turbo Streams, and progressive enhancement of server-rendered HTML applications.
---

# Stimulus & Hotwire

This skill should be used when building interactive server-rendered applications with Stimulus and Hotwire. It covers controllers, Turbo Drive, Turbo Frames, Turbo Streams, and progressive enhancement.

## When to Use This Skill

Use this skill when you need to:

- Add JavaScript behavior to server-rendered HTML
- Use Turbo for fast page navigation without SPA
- Stream partial page updates from the server
- Build interactive UIs with Rails, Laravel, or Django
- Progressively enhance HTML with controllers

## Stimulus Controllers

```javascript
// controllers/counter_controller.js
import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
  static targets = ["count", "output"];
  static values = {
    count: { type: Number, default: 0 },
    max: Number,
  };
  static classes = ["active"];

  connect() {
    console.log("Counter connected");
  }

  increment() {
    if (this.maxValue && this.countValue >= this.maxValue) return;
    this.countValue++;
  }

  decrement() {
    if (this.countValue > 0) this.countValue--;
  }

  countValueChanged() {
    this.countTarget.textContent = this.countValue;
    this.outputTarget.classList.toggle(this.activeClass, this.countValue > 0);
  }
}
```

```html
<div data-controller="counter" data-counter-count-value="5" data-counter-max-value="10" data-counter-active-class="text-blue-500">
  <span data-counter-target="count">5</span>
  <div data-counter-target="output">
    <button data-action="click->counter#increment">+</button>
    <button data-action="click->counter#decrement">-</button>
  </div>
</div>
```

## Actions and Events

```html
<!-- Click action -->
<button data-action="click->modal#open">Open Modal</button>

<!-- Multiple actions -->
<input
  data-action="input->search#query keydown.enter->search#submit focus->search#highlight"
/>

<!-- Action with params -->
<button
  data-action="click->cart#add"
  data-cart-id-param="123"
  data-cart-name-param="Widget"
  data-cart-price-param="9.99"
>
  Add to Cart
</button>
```

```javascript
// controllers/cart_controller.js
export default class extends Controller {
  add({ params: { id, name, price } }) {
    console.log(`Adding ${name} ($${price}) with id ${id}`);
  }
}
```

## Outlets (Controller Communication)

```javascript
// controllers/form_controller.js
export default class extends Controller {
  static outlets = ["validation"];

  submit() {
    if (this.validationOutlets.every((v) => v.isValid)) {
      this.element.submit();
    }
  }
}

// controllers/validation_controller.js
export default class extends Controller {
  static targets = ["input", "error"];
  static values = { required: Boolean };

  get isValid() {
    if (this.requiredValue && !this.inputTarget.value) {
      this.errorTarget.textContent = "Required";
      return false;
    }
    this.errorTarget.textContent = "";
    return true;
  }
}
```

```html
<form data-controller="form" data-form-validation-outlet=".field-validation">
  <div data-controller="validation" data-validation-required-value="true" class="field-validation">
    <input data-validation-target="input" data-action="blur->validation#validate" />
    <span data-validation-target="error"></span>
  </div>
  <button data-action="click->form#submit">Submit</button>
</form>
```

## Turbo Drive

```html
<!-- Turbo Drive is automatic for all links and forms -->
<!-- Opt out specific links -->
<a href="/download" data-turbo="false">Download PDF</a>

<!-- Persist elements across navigations -->
<div id="player" data-turbo-permanent>
  <audio src="song.mp3"></audio>
</div>

<!-- Advance vs replace history -->
<a href="/page" data-turbo-action="replace">Replace in history</a>
```

## Turbo Frames

```html
<!-- Lazy-loaded frame -->
<turbo-frame id="user-profile" src="/users/1/profile" loading="lazy">
  <p>Loading profile...</p>
</turbo-frame>

<!-- Frame that targets itself -->
<turbo-frame id="search-results">
  <form action="/search" method="get">
    <input name="q" />
    <button>Search</button>
  </form>
  <div class="results">
    <!-- Results replaced here -->
  </div>
</turbo-frame>

<!-- Break out of frame -->
<turbo-frame id="messages">
  <a href="/messages/1">View (stays in frame)</a>
  <a href="/messages/1" data-turbo-frame="_top">View (full page)</a>
</turbo-frame>
```

## Turbo Streams

```html
<!-- Server sends these in response to form submissions or via WebSocket -->

<!-- Append -->
<turbo-stream action="append" target="messages">
  <template>
    <div id="message_1">New message</div>
  </template>
</turbo-stream>

<!-- Prepend -->
<turbo-stream action="prepend" target="notifications">
  <template>
    <div>New notification</div>
  </template>
</turbo-stream>

<!-- Replace -->
<turbo-stream action="replace" target="user_1">
  <template>
    <div id="user_1">Updated user data</div>
  </template>
</turbo-stream>

<!-- Remove -->
<turbo-stream action="remove" target="message_5"></turbo-stream>

<!-- Update (innerHTML only) -->
<turbo-stream action="update" target="counter">
  <template>42</template>
</turbo-stream>
```

```ruby
# Rails controller example
def create
  @message = Message.create!(message_params)
  respond_to do |format|
    format.turbo_stream
    format.html { redirect_to messages_path }
  end
end

# app/views/messages/create.turbo_stream.erb
<%= turbo_stream.append "messages", @message %>
<%= turbo_stream.update "message_count", Message.count %>
```

## Additional Resources

- Stimulus: https://stimulus.hotwired.dev/
- Turbo: https://turbo.hotwired.dev/
- Hotwire: https://hotwired.dev/
