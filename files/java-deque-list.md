# Java的Deque和List关系图

Below is a UML class diagram in Mermaid syntax that illustrates the relationships between Java's `Deque`, `List`, `ArrayList`, and related interfaces and classes in the Java Collections Framework. The diagram includes key interfaces like `Collection`, `List`, `Deque`, and `Queue`, and concrete classes like `ArrayList`, `LinkedList`, and `ArrayDeque`, showing their inheritance and implementation relationships.

```mermaid
classDiagram
    class Collection {
        <<interface>>
        +add(E)
        +remove(Object)
        +size()
    }
    
    class Iterable {
        <<interface>>
        +iterator()
    }
    
    class Queue {
        <<interface>>
        +offer(E)
        +poll()
        +peek()
    }
    
    class Deque {
        <<interface>>
        +addFirst(E)
        +addLast(E)
        +pollFirst()
        +pollLast()
    }
    
    class List {
        <<interface>>
        +get(int)
        +set(int, E)
        +add(int, E)
        +remove(int)
    }
    
    class ArrayList {
        -Object[] elementData
        +get(int)
        +set(int, E)
        +add(E)
        +remove(int)
    }
    
    class LinkedList {
        -Node first
        -Node last
        +get(int)
        +addFirst(E)
        +addLast(E)
        +pollFirst()
        +pollLast()
    }
    
    class ArrayDeque {
        -Object[] elements
        +addFirst(E)
        +addLast(E)
        +pollFirst()
        +pollLast()
    }
    
    Iterable <|.. Collection
    Collection <|.. Queue
    Collection <|.. List
    Queue <|.. Deque
    List <|.. ArrayList
    List <|.. LinkedList
    Deque <|.. LinkedList
    Deque <|.. ArrayDeque
    Queue <|.. ArrayDeque

    note for Collection "Root interface for all collections"
    note for List "Ordered collection with index-based access"
    note for Deque "Double-ended queue, supports adding/removing from both ends"
    note for ArrayList "Resizable array implementation of List"
    note for LinkedList "Doubly-linked list implementation of List and Deque"
    note for ArrayDeque "Resizable array implementation of Deque"

```
