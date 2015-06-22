# Senior Design Project Ideas
I can't come up with my own ideas for a senior design project, so I made a website where other people can post their ideas.

## MongoDB
Stuff required on the database.

### Collections
MongoDB collections

#### People
- keys
  - _id (ObjectId)
  - firstName (string)
  - lastName (string)
  - fullName (string)
  - major (string)
  - interests (array of strings)
  - photo (string)
  - type (string) (student/adviser)
  - joined (ISODate or Number)
  - email (string)

#### Projects
- keys
  - _id (ObjectId)
  - title (string)
  - iconURL (string)
  - link (string)
  - team (array of ObjectIds)

## Dependencies
- https://select2.github.io/
- Flask
- pymongo