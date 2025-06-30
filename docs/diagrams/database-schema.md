# Database Schema Diagram

```mermaid
erDiagram
    Users ||--o{ Rides : creates
    Users ||--o{ RideRequests : makes
    Users ||--o{ Reviews : gives
    Users ||--o{ Reviews : receives
    Rides ||--o{ RideRequests : receives
    Rides ||--o{ RidePassengers : has
    Users ||--o{ RidePassengers : participates
    
    Users {
        int id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        string phone
        date date_of_birth
        enum gender
        text bio
        string profile_picture_url
        boolean is_driver
        string driver_license
        int rating
        int total_rides
        datetime created_at
        datetime updated_at
        boolean is_active
    }
    
    Rides {
        int id PK
        int driver_id FK
        string origin
        string destination
        datetime departure_time
        int available_seats
        decimal price_per_seat
        text description
        string car_model
        string car_color
        string car_license_plate
        enum status
        datetime created_at
        datetime updated_at
    }
    
    RideRequests {
        int id PK
        int ride_id FK
        int passenger_id FK
        text message
        enum status
        datetime created_at
        datetime updated_at
    }
    
    RidePassengers {
        int id PK
        int ride_id FK
        int passenger_id FK
        datetime joined_at
        enum status
    }
    
    Reviews {
        int id PK
        int reviewer_id FK
        int reviewed_id FK
        int ride_id FK
        int rating
        text comment
        datetime created_at
    }
```

## Schema Notes

- **Users**: Core user information including driver capabilities
- **Rides**: Ride offers with details about route, timing, and capacity
- **RideRequests**: Passenger requests to join specific rides
- **RidePassengers**: Confirmed passengers for rides
- **Reviews**: User ratings and feedback system
