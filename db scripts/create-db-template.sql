-- Active: 1687640843759@@127.0.0.1@5432@ufo
CREATE DATABASE ufo;


-- ###### DANGER ZONE
drop table ufo_observation;
drop table ufo_description;

delete from ufo_description;
delete from ufo_observation;
-- #############



create table ufo_description (
    obs_description_id serial primary key,
    obs_ocurred TIME,
    obs_reported TIME,
    obs_summary VARCHAR(300),
    obs_detailed_description varchar(1000)
);

-- TODO : make obs_shape an enumerated
CREATE TYPE shape AS ENUM ('Oval', 'Triangle', 'Light', 'Dark', 'Orb', 'Fireball', 'Circle', 'Changing', 'Disk', 'Cylinder', 'Rectangle', 'Unknown', 'Changing', 'Egg', 'cube', 'Sphere', 'Formation', 'Chevron', 'Flash', 'Disk', 'Star', 'Other', 'Cone');

create table ufo_observation (
    obs_id VARCHAR(32) not null,
    obs_posted DATE,
    obs_city VARCHAR(100),
    obs_state VARCHAR(100),
    obs_country VARCHAR(100),
    obs_shape VARCHAR(50),
    obs_duration VARCHAR(50),
    obs_description_id SERIAL,
    obs_images BOOLEAN default false,
    PRIMARY KEY (obs_id),
    FOREIGN KEY (obs_description_id) REFERENCES ufo_description
);




insert into ufo_description (obs_ocurred, obs_reported, obs_summary, obs_detailed_description) VALUES
('05/19/2023 1:49 AM', '5/19/2023 3:40:01 AM', '9 lights in straight line', 'I was on my way home from work driving on I5 northbound and I happened to noticed a string of lights in a completely straight line and not moving. As I continued to look at them the bottom 2 lights #''s 8&9 slowly faded out and disappeared then in about 5 seconds reappeared. Approx. 1-2 min. later the 3rd light from the top just disappeared for about 2 seconds then suddenly reappeared. About 3 min. into watching the lights they all slowly moved closer together all while staying in a perfectly straight line in the same location in the sky then all of them slowly faded out and never came back.'),
(' 05/18/2023 7:40 PM', '5/18/2023 3:25:04 PM', 'The object changed color', 'Looked out window and saw the sun catching on a bright ball in the sky, it was round and fast. Moving horizontally.

Me and my mother were eating supper when I looked out the window and saw a big object in the sky. I thought it was a plane at first but then it was very fast. I got up from my seat after my mother and went to the window to get a better look. It was a silk white and sometimes shined gray, it moved horizontally, back and fourth quite fast. My mother thinks it was a eagle but I didn''t see any wings or trail behind it. The sky today is clear with a few clouds.'),
('05/18/2023 1:27 PM', '5/19/2023 9:30:44 AM', 'There were lights on the object', 'Saw what looked like a long cigar shaped object and another tiny flashing light zipping around it.

Cigar shape maybe as large as two train cars in length. Floated up and around and down in all directions. Slow moving. Thought it was a balloon but it floated a few times without moving. Then in one of my videos there is a second tiny object with a flashing light zipping around the larger object and then takes off super fast.');


insert into ufo_observation values
('5/19/23 01:49', '5/19/23', 'Harrisburg East of I5', 'OR', 'USA', 'Light', 'Approx. 3-4 min.', 2, false),
('5/18/23 19:40', '5/19/23', 'Kippens', 'NF', 'USA', 'Cigar', '10 minutes', 3, true);
