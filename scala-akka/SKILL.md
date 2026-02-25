---
name: scala-akka
description: Scala Akka patterns covering actor model, typed actors, cluster sharding, event sourcing, streams, HTTP routes, and distributed systems with Akka Toolkit.
---

# Scala Akka

This skill should be used when building distributed systems with Scala and Akka. It covers typed actors, cluster sharding, event sourcing, streams, HTTP, and distributed patterns.

## When to Use This Skill

Use this skill when you need to:

- Build actor-based concurrent systems
- Use Akka Cluster for distributed applications
- Implement event sourcing with Akka Persistence
- Process data streams with Akka Streams
- Create HTTP APIs with Akka HTTP

## Typed Actors

```scala
import akka.actor.typed.{ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors

object UserActor {
  sealed trait Command
  case class GetUser(id: String, replyTo: ActorRef[Response]) extends Command
  case class CreateUser(name: String, email: String, replyTo: ActorRef[Response]) extends Command

  sealed trait Response
  case class UserFound(user: User) extends Response
  case class UserCreated(user: User) extends Response
  case class UserNotFound(id: String) extends Response

  def apply(): Behavior[Command] = Behaviors.setup { context =>
    var users = Map.empty[String, User]

    Behaviors.receiveMessage {
      case GetUser(id, replyTo) =>
        users.get(id) match {
          case Some(user) => replyTo ! UserFound(user)
          case None => replyTo ! UserNotFound(id)
        }
        Behaviors.same

      case CreateUser(name, email, replyTo) =>
        val id = java.util.UUID.randomUUID().toString
        val user = User(id, name, email)
        users = users + (id -> user)
        replyTo ! UserCreated(user)
        Behaviors.same
    }
  }
}
```

## Event Sourcing (Akka Persistence)

```scala
import akka.persistence.typed.scaladsl.{Effect, EventSourcedBehavior}
import akka.persistence.typed.PersistenceId

object AccountEntity {
  sealed trait Command
  case class Deposit(amount: BigDecimal, replyTo: ActorRef[Response]) extends Command
  case class Withdraw(amount: BigDecimal, replyTo: ActorRef[Response]) extends Command
  case class GetBalance(replyTo: ActorRef[Response]) extends Command

  sealed trait Event
  case class Deposited(amount: BigDecimal) extends Event
  case class Withdrawn(amount: BigDecimal) extends Event

  sealed trait Response
  case class Balance(amount: BigDecimal) extends Response
  case object InsufficientFunds extends Response

  case class State(balance: BigDecimal = 0)

  def apply(accountId: String): Behavior[Command] =
    EventSourcedBehavior[Command, Event, State](
      persistenceId = PersistenceId.ofUniqueId(accountId),
      emptyState = State(),
      commandHandler = (state, cmd) => cmd match {
        case Deposit(amount, replyTo) =>
          Effect.persist(Deposited(amount))
            .thenReply(replyTo)(s => Balance(s.balance))

        case Withdraw(amount, replyTo) =>
          if (state.balance >= amount)
            Effect.persist(Withdrawn(amount))
              .thenReply(replyTo)(s => Balance(s.balance))
          else
            Effect.reply(replyTo)(InsufficientFunds)

        case GetBalance(replyTo) =>
          Effect.reply(replyTo)(Balance(state.balance))
      },
      eventHandler = (state, event) => event match {
        case Deposited(amount) => state.copy(balance = state.balance + amount)
        case Withdrawn(amount) => state.copy(balance = state.balance - amount)
      }
    )
}
```

## Akka Streams

```scala
import akka.stream.scaladsl.{Source, Flow, Sink}

val source = Source(1 to 1000)
val flow = Flow[Int]
  .filter(_ % 2 == 0)
  .map(_ * 2)
  .grouped(10)
val sink = Sink.foreach[Seq[Int]](batch => println(s"Batch: $batch"))

source.via(flow).runWith(sink)

// File processing stream
val fileSource = FileIO.fromPath(Paths.get("data.csv"))
val parseFlow = Framing.delimiter(ByteString("\n"), 10000)
  .map(_.utf8String)
  .map(parseCsvLine)
val dbSink = Flow[Record].mapAsync(4)(record => db.insert(record)).toMat(Sink.ignore)(Keep.right)

fileSource.via(parseFlow).runWith(dbSink)
```

## Akka HTTP

```scala
import akka.http.scaladsl.server.Directives._

val route =
  pathPrefix("api" / "users") {
    get {
      parameter("page".as[Int].withDefault(1)) { page =>
        complete(getUsers(page))
      }
    } ~
    post {
      entity(as[CreateUserRequest]) { request =>
        onSuccess(createUser(request)) { user =>
          complete(StatusCodes.Created, user)
        }
      }
    } ~
    path(Segment) { id =>
      get {
        onSuccess(getUser(id)) {
          case Some(user) => complete(user)
          case None => complete(StatusCodes.NotFound)
        }
      }
    }
  }
```

## Additional Resources

- Akka: https://doc.akka.io/
- Akka Streams: https://doc.akka.io/libraries/akka-core/current/stream/
- Akka HTTP: https://doc.akka.io/libraries/akka-http/current/
