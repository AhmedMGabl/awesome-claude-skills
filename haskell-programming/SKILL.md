---
name: haskell-programming
description: Haskell programming patterns covering type classes, monads, functors, algebraic data types, IO, Cabal/Stack build tools, and functional programming idioms.
---

# Haskell Programming

This skill should be used when writing functional programs in Haskell. It covers type classes, monads, ADTs, IO, Cabal/Stack, and idiomatic Haskell patterns.

## When to Use This Skill

Use this skill when you need to:

- Write purely functional programs in Haskell
- Use monads for side effects and composition
- Define algebraic data types and type classes
- Build projects with Cabal or Stack
- Work with IO, concurrency, and error handling

## Basics

```haskell
-- Types and functions
factorial :: Integer -> Integer
factorial 0 = 1
factorial n = n * factorial (n - 1)

-- Pattern matching
describeList :: [a] -> String
describeList xs = case xs of
  []  -> "empty"
  [_] -> "singleton"
  _   -> "longer list with " ++ show (length xs) ++ " elements"

-- Guards
bmiTell :: Double -> String
bmiTell bmi
  | bmi <= 18.5 = "underweight"
  | bmi <= 25.0 = "normal"
  | bmi <= 30.0 = "overweight"
  | otherwise    = "obese"
```

## Algebraic Data Types

```haskell
-- Sum type
data Shape
  = Circle Double
  | Rectangle Double Double
  | Triangle Double Double Double
  deriving (Show, Eq)

area :: Shape -> Double
area (Circle r)        = pi * r * r
area (Rectangle w h)   = w * h
area (Triangle a b c)  = let s = (a + b + c) / 2
                          in sqrt (s * (s-a) * (s-b) * (s-c))

-- Record syntax
data User = User
  { userName  :: String
  , userEmail :: String
  , userAge   :: Int
  } deriving (Show, Eq)

-- Parameterized types
data Tree a = Leaf | Node (Tree a) a (Tree a) deriving (Show)

insert :: Ord a => a -> Tree a -> Tree a
insert x Leaf = Node Leaf x Leaf
insert x (Node left val right)
  | x < val   = Node (insert x left) val right
  | x > val   = Node left val (insert x right)
  | otherwise  = Node left val right
```

## Type Classes

```haskell
class Describable a where
  describe :: a -> String

instance Describable Shape where
  describe (Circle r)      = "Circle with radius " ++ show r
  describe (Rectangle w h) = "Rectangle " ++ show w ++ "x" ++ show h
  describe (Triangle a b c) = "Triangle with sides " ++ show [a,b,c]

-- Deriving common type classes
data Color = Red | Green | Blue
  deriving (Show, Eq, Ord, Enum, Bounded)
```

## Monads and Do Notation

```haskell
import Control.Monad (when, forM_)

-- Maybe monad for safe operations
safeDivide :: Double -> Double -> Maybe Double
safeDivide _ 0 = Nothing
safeDivide x y = Just (x / y)

calculate :: Double -> Double -> Double -> Maybe Double
calculate a b c = do
  ab <- safeDivide a b
  safeDivide ab c

-- IO monad
main :: IO ()
main = do
  putStrLn "Enter your name:"
  name <- getLine
  when (not (null name)) $
    putStrLn ("Hello, " ++ name ++ "!")

-- Either for error handling
data AppError = NotFound String | InvalidInput String deriving (Show)

findUser :: String -> Either AppError User
findUser "admin" = Right (User "admin" "admin@example.com" 30)
findUser name    = Left (NotFound $ "User not found: " ++ name)
```

## Common Patterns

```haskell
import Data.Map (Map)
import qualified Data.Map as Map
import Data.List (sort, group, sortBy)
import Data.Ord (Down(..))

-- Map operations
wordFrequency :: String -> Map String Int
wordFrequency = Map.fromListWith (+) . map (\w -> (w, 1)) . words

-- List comprehensions
pythagoreanTriples :: Int -> [(Int, Int, Int)]
pythagoreanTriples n =
  [ (a, b, c)
  | c <- [1..n], b <- [1..c], a <- [1..b]
  , a*a + b*b == c*c
  ]

-- Higher-order functions
pipeline :: [Int] -> [Int]
pipeline = take 5 . filter even . map (* 2) . sort
```

## Cabal Project

```cabal
-- my-project.cabal
cabal-version: 3.0
name:          my-project
version:       0.1.0.0

executable my-app
  main-is:          Main.hs
  hs-source-dirs:   src
  build-depends:    base ^>=4.17, text, containers, aeson
  default-language: Haskell2010
  ghc-options:      -Wall -O2

library
  exposed-modules:  MyLib
  hs-source-dirs:   src
  build-depends:    base ^>=4.17
  default-language: Haskell2010

test-suite tests
  type:             exitcode-stdio-1.0
  main-is:          Spec.hs
  hs-source-dirs:   test
  build-depends:    base, hspec, my-project
  default-language: Haskell2010
```

## Testing

```haskell
-- test/Spec.hs
import Test.Hspec

main :: IO ()
main = hspec $ do
  describe "factorial" $ do
    it "returns 1 for 0" $
      factorial 0 `shouldBe` 1
    it "returns 120 for 5" $
      factorial 5 `shouldBe` 120

  describe "safeDivide" $ do
    it "divides normally" $
      safeDivide 10 2 `shouldBe` Just 5.0
    it "returns Nothing for zero" $
      safeDivide 10 0 `shouldBe` Nothing
```

## Additional Resources

- Haskell: https://www.haskell.org/documentation/
- Learn You a Haskell: http://learnyouahaskell.com/
- Cabal: https://cabal.readthedocs.io/
