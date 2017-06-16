#! /bin/bash
CATCH_DB=naomi7
CATCH_DB_PORT=5433
CATCH_DB_PWD=moria

# create .pgpass
echo "localhost:${CATCH_DB_PORT}:${CATCH_DB}:posgres:${CATCH_DB_PWD}" > ${PWD}/.pgpass
chmod 600 ${PWD}/.pgpass

# drop and re-create db
PGPASSFILE=${PWD}/.pgpass dropdb -h localhost -p ${CATCH_DB_PORT} -w -U postgres ${CATCH_DB}
PGPASSFILE=${PWD}/.pgpass createdb -h localhost -p ${CATCH_DB_PORT} -w -U postgres ${CATCH_DB}

# load test data
PGPASSFILE=${PWD}/.pgpass psql -h localhost -p ${CATCH_DB_PORT} -w -U postgres \
    ${CATCH_DB} < ${CATCH_DB}_pgdump


