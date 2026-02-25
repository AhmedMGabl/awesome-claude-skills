---
name: nestjs-framework
description: NestJS framework development covering module architecture, controllers and providers, dependency injection, guards and interceptors, pipes and validation, TypeORM/Prisma integration, WebSocket gateways, microservices, Swagger documentation, and testing with Jest.
---

# NestJS Framework

This skill should be used when building server-side applications with NestJS. It covers module architecture, dependency injection, middleware, database integration, and testing patterns.

## When to Use This Skill

Use this skill when you need to:

- Build structured Node.js APIs with NestJS
- Implement dependency injection and modular architecture
- Add authentication guards and request validation
- Set up WebSocket gateways or microservices
- Generate Swagger/OpenAPI documentation

## Module Architecture

```typescript
// app.module.ts
import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { TypeOrmModule } from "@nestjs/typeorm";
import { UsersModule } from "./users/users.module";
import { AuthModule } from "./auth/auth.module";

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRootAsync({
      useFactory: (config: ConfigService) => ({
        type: "postgres",
        url: config.get("DATABASE_URL"),
        autoLoadEntities: true,
        synchronize: config.get("NODE_ENV") !== "production",
      }),
      inject: [ConfigService],
    }),
    UsersModule,
    AuthModule,
  ],
})
export class AppModule {}
```

## Controller + Service Pattern

```typescript
// users/users.controller.ts
import { Controller, Get, Post, Body, Param, UseGuards, Query } from "@nestjs/common";
import { ApiTags, ApiBearerAuth, ApiOperation } from "@nestjs/swagger";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { UsersService } from "./users.service";
import { CreateUserDto } from "./dto/create-user.dto";

@ApiTags("users")
@Controller("users")
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @ApiOperation({ summary: "Create a new user" })
  create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }

  @Get()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  findAll(@Query("page") page = 1, @Query("limit") limit = 20) {
    return this.usersService.findAll(page, limit);
  }

  @Get(":id")
  @UseGuards(JwtAuthGuard)
  findOne(@Param("id") id: string) {
    return this.usersService.findOne(id);
  }
}
```

```typescript
// users/users.service.ts
import { Injectable, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { User } from "./user.entity";

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly usersRepo: Repository<User>,
  ) {}

  async create(dto: CreateUserDto): Promise<User> {
    const user = this.usersRepo.create(dto);
    return this.usersRepo.save(user);
  }

  async findAll(page: number, limit: number) {
    const [items, total] = await this.usersRepo.findAndCount({
      skip: (page - 1) * limit,
      take: limit,
      order: { createdAt: "DESC" },
    });
    return { items, total, page, totalPages: Math.ceil(total / limit) };
  }

  async findOne(id: string): Promise<User> {
    const user = await this.usersRepo.findOne({ where: { id } });
    if (!user) throw new NotFoundException(`User ${id} not found`);
    return user;
  }
}
```

## DTO Validation with Pipes

```typescript
// users/dto/create-user.dto.ts
import { IsEmail, IsString, MinLength, IsOptional, IsEnum } from "class-validator";
import { ApiProperty } from "@nestjs/swagger";

export class CreateUserDto {
  @ApiProperty({ example: "user@example.com" })
  @IsEmail()
  email: string;

  @ApiProperty({ example: "John Doe" })
  @IsString()
  @MinLength(2)
  name: string;

  @ApiProperty({ minLength: 8 })
  @IsString()
  @MinLength(8)
  password: string;

  @ApiProperty({ enum: ["user", "admin"], default: "user" })
  @IsOptional()
  @IsEnum(["user", "admin"])
  role?: string;
}
```

## JWT Authentication Guard

```typescript
// auth/jwt.strategy.ts
import { Injectable } from "@nestjs/common";
import { PassportStrategy } from "@nestjs/passport";
import { ExtractJwt, Strategy } from "passport-jwt";
import { ConfigService } from "@nestjs/config";

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(config: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: config.get("JWT_SECRET"),
    });
  }

  validate(payload: { sub: string; email: string; role: string }) {
    return { id: payload.sub, email: payload.email, role: payload.role };
  }
}

// auth/jwt-auth.guard.ts
import { Injectable } from "@nestjs/common";
import { AuthGuard } from "@nestjs/passport";

@Injectable()
export class JwtAuthGuard extends AuthGuard("jwt") {}
```

## Custom Interceptor

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from "@nestjs/common";
import { Observable, tap } from "rxjs";

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const req = context.switchToHttp().getRequest();
    const now = Date.now();
    return next.handle().pipe(
      tap(() => console.log(`${req.method} ${req.url} — ${Date.now() - now}ms`)),
    );
  }
}
```

## Testing

```typescript
import { Test } from "@nestjs/testing";
import { UsersService } from "./users.service";
import { getRepositoryToken } from "@nestjs/typeorm";
import { User } from "./user.entity";

describe("UsersService", () => {
  let service: UsersService;
  const mockRepo = {
    create: jest.fn((dto) => dto),
    save: jest.fn((user) => Promise.resolve({ id: "1", ...user })),
    findOne: jest.fn(),
    findAndCount: jest.fn(),
  };

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        UsersService,
        { provide: getRepositoryToken(User), useValue: mockRepo },
      ],
    }).compile();
    service = module.get(UsersService);
  });

  it("should create a user", async () => {
    const dto = { email: "test@test.com", name: "Test", password: "12345678" };
    const result = await service.create(dto);
    expect(result).toHaveProperty("id");
    expect(mockRepo.save).toHaveBeenCalled();
  });
});
```

## CLI Commands

```bash
nest new my-api
nest generate module users
nest generate controller users
nest generate service users
nest generate resource orders  # Full CRUD scaffold
```

## Additional Resources

- NestJS docs: https://docs.nestjs.com/
- NestJS recipes: https://docs.nestjs.com/recipes/
- TypeORM integration: https://docs.nestjs.com/techniques/database
