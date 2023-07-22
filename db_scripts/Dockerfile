FROM postgres:latest
ENV POSTGRES_PASSWORD=coding
ENV POSTGRES_USER=coding
# POSTGRES_DB defines the name of the default DB to be created			
ENV POSTGRES_DB=ufo
COPY init_db.sql /docker-entrypoint-initdb.d/init_db.sql