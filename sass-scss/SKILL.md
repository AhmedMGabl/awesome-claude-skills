---
name: sass-scss
description: Sass/SCSS patterns covering variables, mixins, functions, nesting, modules, partials, extend/placeholder selectors, and responsive design utilities.
---

# Sass/SCSS

This skill should be used when writing stylesheets with Sass/SCSS. It covers variables, mixins, functions, modules, partials, and responsive utilities.

## When to Use This Skill

Use this skill when you need to:

- Write maintainable CSS with variables and mixins
- Organize styles with partials and modules
- Create responsive design utilities
- Use functions for calculations and color manipulation
- Build design systems with Sass

## Variables and Nesting

```scss
// _variables.scss
$primary: #0066cc;
$secondary: #6c757d;
$font-stack: "Inter", system-ui, sans-serif;
$spacing: (xs: 0.25rem, sm: 0.5rem, md: 1rem, lg: 1.5rem, xl: 2rem);
$breakpoints: (sm: 576px, md: 768px, lg: 992px, xl: 1200px);

// Nesting
.card {
  padding: map-get($spacing, md);
  border-radius: 8px;

  &__header {
    font-weight: 600;
    border-bottom: 1px solid lighten($secondary, 40%);
  }

  &__body {
    padding: map-get($spacing, md) 0;
  }

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  &--featured {
    border: 2px solid $primary;
  }
}
```

## Mixins

```scss
// _mixins.scss
@mixin respond-to($breakpoint) {
  $value: map-get($breakpoints, $breakpoint);
  @if $value {
    @media (min-width: $value) { @content; }
  }
}

@mixin flex-center($direction: row) {
  display: flex;
  flex-direction: $direction;
  align-items: center;
  justify-content: center;
}

@mixin truncate($lines: 1) {
  @if $lines == 1 {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

// Usage
.hero {
  @include flex-center(column);
  padding: 2rem;

  @include respond-to(md) {
    padding: 4rem;
  }
}

.title {
  @include truncate(2);
}
```

## Functions

```scss
// _functions.scss
@function rem($px) {
  @return calc($px / 16) * 1rem;
}

@function shade($color, $amount) {
  @return mix(black, $color, $amount);
}

@function tint($color, $amount) {
  @return mix(white, $color, $amount);
}

@function spacing($key) {
  @return map-get($spacing, $key);
}

// Usage
.element {
  font-size: rem(18);
  padding: spacing(md);
  background: tint($primary, 90%);
  border: 1px solid shade($primary, 20%);
}
```

## Modules (@use and @forward)

```scss
// _index.scss (barrel file)
@forward "variables";
@forward "mixins";
@forward "functions";

// component.scss
@use "index" as *;
@use "sass:math";
@use "sass:color";

.component {
  width: math.div(100%, 3);
  color: color.adjust($primary, $lightness: -10%);
  padding: spacing(lg);

  @include respond-to(md) {
    width: math.div(100%, 4);
  }
}
```

## Extend and Placeholders

```scss
%visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
}

%button-base {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary {
  @extend %button-base;
  background: $primary;
  color: white;
}

.sr-only {
  @extend %visually-hidden;
}
```

## Loops and Conditionals

```scss
// Generate utility classes
@each $name, $value in $spacing {
  .p-#{$name} { padding: $value; }
  .m-#{$name} { margin: $value; }
  .mt-#{$name} { margin-top: $value; }
  .mb-#{$name} { margin-bottom: $value; }
}

// Color palette generation
$colors: (primary: $primary, secondary: $secondary, success: #28a745, danger: #dc3545);

@each $name, $color in $colors {
  .bg-#{$name} { background-color: $color; }
  .text-#{$name} { color: $color; }
  @for $i from 1 through 9 {
    .bg-#{$name}-#{$i * 100} {
      background-color: mix(white, $color, (10 - $i) * 10%);
    }
  }
}
```

## Additional Resources

- Sass: https://sass-lang.com/documentation/
- Sass Modules: https://sass-lang.com/blog/the-module-system-is-launched
- Sass Guidelines: https://sass-guidelin.es/
