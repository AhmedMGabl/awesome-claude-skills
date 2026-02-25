---
name: grpc-protobuf
description: gRPC and Protocol Buffers implementation covering proto3 schema definition, code generation, unary and streaming RPCs, interceptors, error handling with status codes, deadlines, load balancing, health checks, and Node.js/Go/Python client-server patterns for microservice communication.
---

# gRPC & Protocol Buffers

This skill should be used when building high-performance microservice communication with gRPC and Protocol Buffers. It covers schema design, code generation, streaming, and production patterns.

## When to Use This Skill

Use this skill when you need to:

- Define service contracts with Protocol Buffers
- Build high-performance inter-service communication
- Implement streaming RPCs (server, client, bidirectional)
- Add interceptors for auth, logging, tracing
- Handle gRPC errors and deadlines
- Generate typed clients from proto definitions

## Proto3 Schema Definition

```protobuf
// proto/user_service.proto
syntax = "proto3";

package userservice.v1;

option go_package = "github.com/myorg/api/gen/userservice/v1";

import "google/protobuf/timestamp.proto";
import "google/protobuf/field_mask.proto";

service UserService {
  // Unary RPC
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc UpdateUser(UpdateUserRequest) returns (User);
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);

  // Server streaming — returns a stream of results
  rpc ListUsers(ListUsersRequest) returns (stream User);

  // Bidirectional streaming
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message User {
  string id = 1;
  string email = 2;
  string display_name = 3;
  Role role = 4;
  google.protobuf.Timestamp created_at = 5;
}

enum Role {
  ROLE_UNSPECIFIED = 0;
  ROLE_USER = 1;
  ROLE_ADMIN = 2;
}

message GetUserRequest {
  string id = 1;
}

message CreateUserRequest {
  string email = 1;
  string display_name = 2;
  Role role = 3;
}

message UpdateUserRequest {
  User user = 1;
  google.protobuf.FieldMask update_mask = 2;
}

message DeleteUserRequest { string id = 1; }
message DeleteUserResponse {}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
}

message ChatMessage {
  string sender_id = 1;
  string content = 2;
  google.protobuf.Timestamp timestamp = 3;
}
```

## Go Server Implementation

```go
package main

import (
    "context"
    "log"
    "net"

    pb "github.com/myorg/api/gen/userservice/v1"
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    "google.golang.org/grpc/health"
    healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

type userServer struct {
    pb.UnimplementedUserServiceServer
    store UserStore
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    if req.Id == "" {
        return nil, status.Error(codes.InvalidArgument, "id is required")
    }

    user, err := s.store.Get(ctx, req.Id)
    if err != nil {
        return nil, status.Error(codes.NotFound, "user not found")
    }
    return user, nil
}

func (s *userServer) ListUsers(req *pb.ListUsersRequest, stream pb.UserService_ListUsersServer) error {
    users, err := s.store.List(stream.Context(), req.Filter, int(req.PageSize))
    if err != nil {
        return status.Error(codes.Internal, "failed to list users")
    }

    for _, user := range users {
        if err := stream.Send(user); err != nil {
            return err
        }
    }
    return nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")

    server := grpc.NewServer(
        grpc.UnaryInterceptor(loggingInterceptor),
        grpc.StreamInterceptor(streamLoggingInterceptor),
    )
    pb.RegisterUserServiceServer(server, &userServer{store: NewUserStore()})

    // Health check
    healthServer := health.NewServer()
    healthpb.RegisterHealthServer(server, healthServer)
    healthServer.SetServingStatus("userservice.v1.UserService", healthpb.HealthCheckResponse_SERVING)

    log.Println("gRPC server listening on :50051")
    log.Fatal(server.Serve(lis))
}

// Unary interceptor for logging
func loggingInterceptor(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
    log.Printf("RPC: %s", info.FullMethod)
    resp, err := handler(ctx, req)
    if err != nil {
        log.Printf("RPC error: %s — %v", info.FullMethod, err)
    }
    return resp, err
}
```

## Node.js Client with nice-grpc

```typescript
// client.ts
import { createChannel, createClient, Metadata } from "nice-grpc";
import { UserServiceDefinition } from "./gen/user_service";

const channel = createChannel("localhost:50051");
const client = createClient(UserServiceDefinition, channel);

// Unary call with deadline
async function getUser(id: string) {
  const user = await client.getUser(
    { id },
    { deadline: Date.now() + 5000 },  // 5 second deadline
  );
  return user;
}

// Server streaming
async function listAllUsers() {
  const users: User[] = [];
  for await (const user of client.listUsers({ pageSize: 100, pageToken: "", filter: "" })) {
    users.push(user);
  }
  return users;
}

// With auth metadata
async function getProtectedUser(id: string, token: string) {
  const metadata = new Metadata();
  metadata.set("authorization", `Bearer ${token}`);
  return client.getUser({ id }, { metadata });
}
```

## Python Client

```python
import grpc
from gen import user_service_pb2 as pb2
from gen import user_service_pb2_grpc as pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = pb2_grpc.UserServiceStub(channel)

# Unary call with timeout
try:
    user = stub.GetUser(pb2.GetUserRequest(id="user-123"), timeout=5.0)
    print(f"User: {user.display_name}")
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print("User not found")
    elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        print("Request timed out")

# Server streaming
for user in stub.ListUsers(pb2.ListUsersRequest(page_size=50)):
    print(user.email)
```

## Code Generation

```bash
# Install protoc plugins
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Generate Go code
protoc --go_out=gen --go-grpc_out=gen proto/user_service.proto

# Generate TypeScript (using ts-proto)
protoc --plugin=protoc-gen-ts_proto=./node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=gen --ts_proto_opt=outputServices=nice-grpc \
  proto/user_service.proto

# Generate Python
python -m grpc_tools.protoc -I. --python_out=gen --grpc_python_out=gen proto/user_service.proto
```

## Additional Resources

- gRPC docs: https://grpc.io/docs/
- Proto3 language guide: https://protobuf.dev/programming-guides/proto3/
- nice-grpc (TypeScript): https://github.com/deeplay-io/nice-grpc
- Buf (proto management): https://buf.build/
