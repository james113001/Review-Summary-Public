# SQL and NLP Pipeline Setup
Contains Docker container for setting up data schema and seed, and the pipeline to Python to create a summary for a given ID using local LLM (Mistral)    
Arbitrarily set port as 15432 to avoid conflict with 5432- you may need to set a different port in yml if you're already using 15432  


1. Clone the repo  
2. Run `docker-compose up` to spin up the PostgreSQL/Python container 
3. Use `psql` or pgAdmin to connect and explore the schema and sample data
