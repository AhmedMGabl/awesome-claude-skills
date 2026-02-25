---
name: grpc-go
description: Go gRPC patterns covering protobuf definitions, server/client implementation, streaming RPCs, interceptors, error handling, health checks, and TLS configuration.
---

# Go gRPC

This skill should be used when building gRPC services with Go. It covers protobuf definitions, server/client implementation, streaming, interceptors, and error handling.

## When to Use This Skill

Use this skill when you need to:

- Define Protocol Buffer service schemas
- Implement gRPC servers and clients in Go
- Use unary, server, client, and bidirectional streaming
- Add interceptors for logging and auth
- Handle errors with gRPC status codes

## Setup

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
go get google.golang.org/grpc
```

## Protobuf Definition

```protobuf
// proto/user/v1/user.proto
syntax = "proto3";
package user.v1;
option go_package = "myapp/gen/user/v1;userv1";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
  rpc StreamUsers(StreamUsersRequest) returns (stream User);
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  string role = 4;
}

message GetUserRequest { string id = 1; }
message GetUserResponse { User user = 1; }

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}
message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}
message CreateUserResponse { User user = 1; }

message StreamUsersRequest { string role = 1; }
```

## Generate Code

```bash
protoc --go_out=. --go-grpc_out=. proto/user/v1/user.proto
```

## Server Implementation

```go
package main

import (
    "context"
    "log"
    "net"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    userv1 "myapp/gen/user/v1"
)

type userServer struct {
    userv1.UnimplementedUserServiceServer
    repo UserRepository
}

func (s *userServer) GetUser(ctx context.Context, req *userv1.GetUserRequest) (*userv1.GetUserResponse, error) {
    user, err := s.repo.GetByID(ctx, req.Id)
    if err != nil {
        return nil, status.Errorf(codes.NotFound, "user %s not found", req.Id)
    }
    return &userv1.GetUserResponse{User: toProto(user)}, nil
}

func (s *userServer) CreateUser(ctx context.Context, req *userv1.CreateUserRequest) (*userv1.CreateUserResponse, error) {
    if req.Name == "" || req.Email == "" {
        return nil, status.Error(codes.InvalidArgument, "name and email required")
    }
    user, err := s.repo.Create(ctx, req.Name, req.Email)
    if err != nil {
        return nil, status.Errorf(codes.Internal, "failed to create: %v", err)
    }
    return &userv1.CreateUserResponse{User: toProto(user)}, nil
}

func (s *userServer) StreamUsers(req *userv1.StreamUsersRequest, stream userv1.UserService_StreamUsersServer) error {
    users, err := s.repo.ListByRole(stream.Context(), req.Role)
    if err != nil {
        return status.Errorf(codes.Internal, "failed to list: %v", err)
    }
    for _, u := range users {
        if err := stream.Send(toProto(u)); err != nil {
            return err
        }
    }
    return nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    srv := grpc.NewServer()
    userv1.RegisterUserServiceServer(srv, &userServer{})
    log.Fatal(srv.Serve(lis))
}
```

## Client

```go
conn, err := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
defer conn.Close()

client := userv1.NewUserServiceClient(conn)

resp, err := client.GetUser(ctx, &userv1.GetUserRequest{Id: "1"})
if err != nil {
    st, _ := status.FromError(err)
    log.Printf("code: %s, msg: %s", st.Code(), st.Message())
}
```

## Interceptors

```go
func loggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    start := time.Now()
    resp, err := handler(ctx, req)
    log.Printf("%s %v %v", info.FullMethod, time.Since(start), err)
    return resp, err
}

srv := grpc.NewServer(grpc.UnaryInterceptor(loggingInterceptor))
```

## Additional Resources

- gRPC Go: https://grpc.io/docs/languages/go/
- Protobuf: https://protobuf.dev/
- gRPC Status: https://grpc.io/docs/guides/status-codes/
