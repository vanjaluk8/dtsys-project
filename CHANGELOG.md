## [3.1.0] - 2024-02-10
- added a new endpoint for the rapidAPI, now it is possible to get the data for the specific stock
- grafana iplementation for the data visualization
- added a new docker container for grafana
- 
## [3.0.0] - 2024-02-04
### Added, removed, trying some new solutions
- added rapidAPI for yahoo finance data
- more dynamic data manipulation, abandoned boring csv and similar, rapidAPI returns back everything in a json format

## [2.0.0] - 2024-01-29
### Refactored
- removed the concepts before, only docker will be used to spare CPU power
- added mongoDB and mysql docker containers
- added sample data for both databases
- the code part in FASTApi is still under testing, the final application will be designed differently
- locust setup for testing requests

## [1.0.0] - 2023-11-01
### Added
- simple structure and setup
- main.py for fastAPI connection
- data_manipulation.ipynb for data manipulation
### Fixed
- docker-compose and volume persistance for DB-1 docker container
### Documentation
- Updated the main [README.md](README.md) file