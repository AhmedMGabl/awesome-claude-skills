---
name: unreal-blueprints
description: Unreal Engine patterns covering C++ gameplay classes, Blueprints, character movement, GAS ability system, Niagara particles, materials, and multiplayer replication.
---

# Unreal Engine Blueprints & C++

This skill should be used when developing games with Unreal Engine. It covers C++ gameplay classes, Blueprints, character movement, GAS, Niagara particles, materials, and multiplayer.

## When to Use This Skill

Use this skill when you need to:

- Build games with Unreal Engine 5
- Write C++ gameplay classes and Blueprint-callable functions
- Implement character movement and abilities
- Configure Niagara particle effects
- Set up multiplayer replication

## C++ Gameplay Class

```cpp
// MyCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

UCLASS()
class MYGAME_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float MaxHealth = 100.f;

    UPROPERTY(ReplicatedUsing = OnRep_Health, BlueprintReadOnly, Category = "Stats")
    float Health;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class USpringArmComponent* CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class UCameraComponent* FollowCamera;

    UFUNCTION(BlueprintCallable, Category = "Combat")
    void TakeDamage(float DamageAmount, AActor* DamageCauser);

    UFUNCTION(BlueprintImplementableEvent, Category = "Combat")
    void OnDeath();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    UFUNCTION()
    void OnRep_Health();

    void MoveForward(float Value);
    void MoveRight(float Value);

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "Net/UnrealNetwork.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 400.f;
    CameraBoom->bUsePawnControlRotation = true;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    Health = MaxHealth;
}

void AMyCharacter::TakeDamage(float DamageAmount, AActor* DamageCauser)
{
    Health = FMath::Clamp(Health - DamageAmount, 0.f, MaxHealth);
    if (Health <= 0.f)
    {
        OnDeath();
    }
}

void AMyCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyCharacter, Health);
}

void AMyCharacter::OnRep_Health()
{
    // Update UI on clients when health replicates
}
```

## Enhanced Input System

```cpp
// In SetupPlayerInputComponent
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    if (UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
        EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
        EnhancedInput->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
    }
}

void AMyCharacter::Move(const FInputActionValue& Value)
{
    FVector2D MovementVector = Value.Get<FVector2D>();
    FRotator Rotation = Controller->GetControlRotation();
    FRotator YawRotation(0, Rotation.Yaw, 0);

    FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
    FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

    AddMovementInput(ForwardDirection, MovementVector.Y);
    AddMovementInput(RightDirection, MovementVector.X);
}
```

## Component Architecture

```cpp
// HealthComponent.h
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UHealthComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float MaxHealth = 100.f;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnHealthChanged, float, NewHealth, float, DamageAmount);

    UPROPERTY(BlueprintAssignable)
    FOnHealthChanged OnHealthChanged;

    UFUNCTION(BlueprintCallable)
    void ApplyDamage(float Amount);

    UFUNCTION(BlueprintCallable)
    void Heal(float Amount);

    UFUNCTION(BlueprintPure)
    float GetHealthPercent() const { return CurrentHealth / MaxHealth; }

private:
    float CurrentHealth;
};
```

## Data-Driven Design with Data Assets

```cpp
UCLASS(BlueprintType)
class UWeaponData : public UDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString WeaponName;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float BaseDamage;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float FireRate;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    TSubclassOf<AActor> ProjectileClass;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    UAnimMontage* FireMontage;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    USoundBase* FireSound;
};
```

## Additional Resources

- UE5 Docs: https://docs.unrealengine.com/
- C++ API Reference: https://docs.unrealengine.com/API/
- UE5 Learning: https://dev.epicgames.com/community/learning
