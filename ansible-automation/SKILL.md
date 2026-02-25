---
name: ansible-automation
description: Ansible automation covering playbooks, roles, inventory management, variables, handlers, templates, Ansible Vault secrets, Galaxy collections, and CI/CD integration for infrastructure provisioning.
---

# Ansible Automation

This skill should be used when the user needs to write or manage Ansible automation for infrastructure provisioning, configuration management, or application deployment. It covers playbooks, roles, inventory, variables, handlers, Jinja2 templates, Vault secrets, Galaxy collections, and CI/CD integration.

## When to Use This Skill

- Write playbooks and roles for server configuration or application deployment
- Manage INI or YAML inventory files, static or dynamic
- Encrypt secrets with Ansible Vault
- Render config files with Jinja2 templates
- Install community content from Ansible Galaxy
- Integrate Ansible into GitHub Actions or GitLab CI pipelines

## Inventory Files

```ini
# inventory/hosts.ini  (INI format)
[webservers]
web1.example.com ansible_user=ubuntu
web2.example.com ansible_user=ubuntu
[production:children]
webservers
[production:vars]
env=production
```

```yaml
# inventory/hosts.yml  (YAML format)
all:
  children:
    webservers:
      hosts:
        web1.example.com: { ansible_user: ubuntu }
        web2.example.com: { ansible_user: ubuntu }
      vars: { app_port: 8080 }
```

## Playbook Structure

```yaml
# site.yml
---
- name: Configure web servers
  hosts: webservers
  become: true
  vars:
    app_port: 8080
  pre_tasks:
    - name: Update apt cache
      ansible.builtin.apt: { update_cache: true, cache_valid_time: 3600 }
  roles:
    - common
    - nginx
  post_tasks:
    - name: Verify nginx is running
      ansible.builtin.service: { name: nginx, state: started }
```

## Roles and Directory Layout

```
roles/nginx/
├── defaults/main.yml   # low-precedence defaults
├── vars/main.yml       # high-precedence role vars
├── tasks/main.yml      # task list
├── handlers/main.yml   # handlers
├── templates/          # Jinja2 templates (.j2)
└── files/              # static files
```

```yaml
# roles/nginx/tasks/main.yml
---
- name: Install nginx
  ansible.builtin.package: { name: nginx, state: present }

- name: Deploy nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: "0644"
  notify: Reload nginx
```

## Variables and Precedence

Precedence (lowest to highest): role defaults, group_vars, host_vars, playbook vars, role vars, extra vars (`-e`).

```yaml
# group_vars/webservers.yml
app_version: "2.1.0"
app_port: 8080
# host_vars/web1.example.com.yml
app_port: 9090   # overrides group var for this host only
```

## Handlers and Notifications

Handlers run once at the end of a play when notified by a task. Define in `handlers/main.yml` and trigger via `notify`:

```yaml
# handlers/main.yml
- name: Reload nginx
  ansible.builtin.service: { name: nginx, state: reloaded }

- name: Restart app
  ansible.builtin.systemd:
    name: myapp
    state: restarted
    daemon_reload: true

# In tasks — triggers handler by name on change
- name: Update TLS certificate
  ansible.builtin.copy:
    src: files/cert.pem
    dest: /etc/ssl/certs/cert.pem
  notify: Reload nginx
```

## Jinja2 Templates

```jinja2
{# templates/nginx.conf.j2 #}
worker_processes {{ ansible_processor_vcpus | default(2) }};
events { worker_connections {{ max_connections }}; }

http {
  server {
    listen {{ app_port }};
    server_name {{ ansible_fqdn }};
    location / { proxy_pass http://127.0.0.1:{{ backend_port }}; }

    {% if ssl_enabled | default(false) %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}
  }
}
```

## Ansible Vault for Secrets

```bash
ansible-vault encrypt group_vars/production/vault.yml   # encrypt file
ansible-vault edit   group_vars/production/vault.yml    # edit in-place
ansible-playbook site.yml --vault-password-file ~/.vault_pass
ansible-vault encrypt_string 'supersecret' --name 'db_password'  # inline
```

Prefix vault variables with `vault_` and reference via plain wrappers:

```yaml
# vault.yml (encrypted)          # vars.yml (plain)
vault_db_password: "s3cr3t"      db_password: "{{ vault_db_password }}"
```

## Galaxy Collections

```yaml
# requirements.yml
collections:
  - { name: community.postgresql, version: ">=3.0.0" }
  - { name: community.docker,     version: "3.4.0" }
roles:
  - { name: geerlingguy.nginx, version: "3.2.0" }
```

```bash
ansible-galaxy collection install -r requirements.yml
ansible-galaxy role install -r requirements.yml
```

Use collection modules by fully qualified name:

```yaml
- name: Create database
  community.postgresql.postgresql_db: { name: myapp, state: present }
  become_user: postgres
```

## CI/CD Integration

```yaml
# .github/workflows/ansible.yml
name: Ansible Deploy
on:
  push: { branches: [main], paths: ["ansible/**"] }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ansible ansible-lint
      - run: ansible-galaxy install -r ansible/requirements.yml
      - name: Write vault password and SSH key
        run: |
          echo "${{ secrets.VAULT_PASSWORD }}" > ~/.vault_pass
          install -m 600 /dev/null ~/.ssh/deploy_key
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
      - run: ansible-lint ansible/site.yml
      - run: |
          ansible-playbook ansible/site.yml \
            -i ansible/inventory/hosts.yml \
            --vault-password-file ~/.vault_pass \
            --private-key ~/.ssh/deploy_key
```

## Best Practices

- Prefer Ansible modules over `shell`/`command` to ensure idempotency.
- Use `--check --diff` to preview changes before applying.
- Add tags to tasks for selective execution: `ansible-playbook site.yml --tags deploy`.
- Store role secrets in Vault-encrypted files; never commit plaintext credentials.
- Pin collection versions in `requirements.yml` for reproducible installs.
