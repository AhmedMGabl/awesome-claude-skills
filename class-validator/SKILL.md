---
name: class-validator
description: class-validator patterns covering decorator-based validation, custom validators, validation groups, conditional validation, nested objects, and NestJS integration.
---

# class-validator

This skill should be used when validating class instances with decorators. It covers validation decorators, custom validators, groups, conditional logic, and NestJS integration.

## When to Use This Skill

Use this skill when you need to:

- Validate class instances using decorators
- Create custom validation decorators
- Apply conditional and grouped validation
- Validate nested objects and arrays
- Integrate with NestJS DTOs

## Setup

```bash
npm install class-validator class-transformer
```

## Basic Validation

```ts
import {
  validate, IsString, IsEmail, IsInt, Min, Max,
  IsEnum, IsOptional, IsBoolean, Length, IsArray,
} from "class-validator";

enum UserRole {
  Admin = "admin",
  User = "user",
  Editor = "editor",
}

class CreateUserDto {
  @IsString()
  @Length(2, 50)
  name!: string;

  @IsEmail()
  email!: string;

  @IsInt()
  @Min(18)
  age!: number;

  @IsEnum(UserRole)
  role!: UserRole;

  @IsOptional()
  @IsString()
  @Length(0, 500)
  bio?: string;

  @IsArray()
  @IsString({ each: true })
  tags!: string[];

  @IsBoolean()
  isActive!: boolean;
}

// Validate
const user = Object.assign(new CreateUserDto(), inputData);
const errors = await validate(user);

if (errors.length > 0) {
  const messages = errors.map((err) => ({
    property: err.property,
    constraints: err.constraints,
  }));
  console.log("Validation errors:", messages);
} else {
  console.log("Valid user:", user);
}
```

## Custom Validators

```ts
import {
  ValidatorConstraint, ValidatorConstraintInterface,
  ValidationArguments, registerDecorator,
} from "class-validator";

@ValidatorConstraint({ async: false })
class IsStrongPasswordConstraint implements ValidatorConstraintInterface {
  validate(password: string) {
    return (
      password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[^a-zA-Z0-9]/.test(password)
    );
  }

  defaultMessage() {
    return "Password must be 8+ chars with uppercase, number, and special character";
  }
}

function IsStrongPassword() {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName,
      validator: IsStrongPasswordConstraint,
    });
  };
}

// Use it
class RegisterDto {
  @IsEmail()
  email!: string;

  @IsStrongPassword()
  password!: string;
}
```

## Nested Validation

```ts
import { ValidateNested, Type } from "class-transformer";
import { IsString, IsNumber, IsArray, validate } from "class-validator";

class AddressDto {
  @IsString()
  street!: string;

  @IsString()
  city!: string;

  @IsString()
  zip!: string;
}

class OrderItemDto {
  @IsString()
  productId!: string;

  @IsNumber()
  quantity!: number;

  @IsNumber()
  price!: number;
}

class CreateOrderDto {
  @ValidateNested()
  @Type(() => AddressDto)
  shippingAddress!: AddressDto;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items!: OrderItemDto[];
}
```

## Validation Groups

```ts
import { IsString, IsEmail, Length, validate } from "class-validator";

class UserDto {
  @IsString({ groups: ["create", "update"] })
  @Length(2, 50, { groups: ["create", "update"] })
  name!: string;

  @IsEmail({}, { groups: ["create"] })
  email!: string;

  @IsString({ groups: ["create"] })
  password!: string;
}

// Validate for create
const createErrors = await validate(user, { groups: ["create"] });

// Validate for update (skips email and password)
const updateErrors = await validate(user, { groups: ["update"] });
```

## NestJS Integration

```ts
import { Controller, Post, Body, UsePipes, ValidationPipe } from "@nestjs/common";

@Controller("users")
class UsersController {
  @Post()
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }
}

// Global validation pipe (main.ts)
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true,        // Strip non-decorated properties
    forbidNonWhitelisted: true, // Throw on unknown properties
    transform: true,        // Auto-transform payloads to DTO instances
    transformOptions: {
      enableImplicitConversion: true,
    },
  })
);
```

## Additional Resources

- class-validator: https://github.com/typestack/class-validator
- Decorators: https://github.com/typestack/class-validator#validation-decorators
- class-transformer: https://github.com/typestack/class-transformer
