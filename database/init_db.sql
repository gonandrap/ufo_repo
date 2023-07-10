-- Active: 1687640843759@@127.0.0.1@5432@ufo

create table if not EXISTS ufo_observation (
    obs_id VARCHAR(32) not null,
    obs_posted DATE,
    obs_city VARCHAR(100),
    obs_state VARCHAR(100),
    obs_country VARCHAR(100),
    obs_shape VARCHAR(50),
    obs_duration VARCHAR(50),
    obs_images BOOLEAN default false,
    PRIMARY KEY (obs_id)
);

create table if not EXISTS ufo_description (
    obs_id VARCHAR(32) not null,
    obs_ocurred TIME,
    obs_reported TIME,
    obs_summary TEXT,
    obs_detailed_description TEXT,
    PRIMARY KEY (obs_id),
    FOREIGN KEY (obs_id) REFERENCES ufo_observation
);

-- CREATE TYPE shape AS ENUM if not EXISTS ('Oval', 'Triangle', 'Light', 'Dark', 'Orb', 'Fireball', 'Circle', 'Changing', 'Disk', 'Cylinder', 'Rectangle', 'Unknown', 'Changing', 'Egg', 'cube', 'Sphere', 'Formation', 'Chevron', 'Flash', 'Disk', 'Star', 'Other', 'Cone');

