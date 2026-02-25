---
name: php-composer
description: PHP Composer patterns covering dependency management, autoloading, package publishing, version constraints, scripts, private repositories, and monorepo configuration.
---

# PHP Composer

This skill should be used when managing PHP projects with Composer. It covers dependency management, autoloading, publishing, version constraints, scripts, and repositories.

## When to Use This Skill

Use this skill when you need to:

- Manage PHP project dependencies
- Configure autoloading (PSR-4, classmap)
- Publish packages to Packagist
- Set up private repositories
- Create Composer scripts and plugins

## composer.json

```json
{
    "name": "mycompany/my-app",
    "description": "My PHP application",
    "type": "project",
    "license": "MIT",
    "require": {
        "php": "^8.2",
        "laravel/framework": "^11.0",
        "guzzlehttp/guzzle": "^7.8"
    },
    "require-dev": {
        "phpunit/phpunit": "^11.0",
        "phpstan/phpstan": "^1.10",
        "laravel/pint": "^1.13"
    },
    "autoload": {
        "psr-4": {
            "App\\": "app/",
            "Database\\Factories\\": "database/factories/",
            "Database\\Seeders\\": "database/seeders/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\": "tests/"
        }
    },
    "scripts": {
        "test": "phpunit",
        "lint": "pint",
        "analyse": "phpstan analyse",
        "check": [
            "@lint",
            "@analyse",
            "@test"
        ],
        "post-autoload-dump": [
            "Illuminate\\Foundation\\ComposerScripts::postAutoloadDump",
            "@php artisan package:discover --ansi"
        ]
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist",
        "sort-packages": true,
        "allow-plugins": {
            "php-http/discovery": true
        }
    },
    "minimum-stability": "stable",
    "prefer-stable": true
}
```

## Version Constraints

```json
{
    "require": {
        "vendor/package": "^2.0",
        "vendor/exact": "2.1.3",
        "vendor/range": ">=2.0 <3.0",
        "vendor/tilde": "~2.1",
        "vendor/wildcard": "2.1.*",
        "vendor/or": "^2.0 || ^3.0",
        "vendor/stability": "^2.0@beta"
    }
}
```

## Common Commands

```bash
composer install                      # Install from lock file
composer update                       # Update dependencies
composer require vendor/package       # Add dependency
composer require --dev vendor/package # Add dev dependency
composer remove vendor/package        # Remove dependency
composer dump-autoload -o             # Optimize autoloader
composer outdated                     # Show outdated packages
composer show --tree                  # Dependency tree
composer why vendor/package           # Why is package installed
composer validate                     # Validate composer.json
```

## Package Publishing

```json
{
    "name": "mycompany/utils",
    "description": "Utility library",
    "type": "library",
    "license": "MIT",
    "autoload": {
        "psr-4": { "MyCompany\\Utils\\": "src/" }
    },
    "extra": {
        "laravel": {
            "providers": ["MyCompany\\Utils\\UtilsServiceProvider"]
        }
    }
}
```

## Private Repositories

```json
{
    "repositories": [
        {
            "type": "vcs",
            "url": "https://github.com/mycompany/private-package"
        },
        {
            "type": "composer",
            "url": "https://packages.mycompany.com"
        }
    ]
}
```

## Platform Config

```json
{
    "config": {
        "platform": {
            "php": "8.2.0",
            "ext-redis": "6.0.0"
        }
    }
}
```

## Additional Resources

- Composer: https://getcomposer.org/doc/
- Packagist: https://packagist.org/
- Version Constraints: https://getcomposer.org/doc/articles/versions.md
