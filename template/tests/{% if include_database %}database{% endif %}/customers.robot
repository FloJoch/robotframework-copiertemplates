*** Settings ***
Documentation       Hello world for databases: create, change and delete customers (in-memory SQLite).
Resource            ${EXECDIR}/resources/tasks/database_tasks.resource
Resource            ${EXECDIR}/resources/assertions/database_assertions.resource
Test Setup          Start Example Database
Test Teardown       Close Database
Test Tags           database    hello-world


*** Test Cases ***
Created Customer Is Stored
    [Documentation]    A created customer is stored with the city.
    Create Customer    Ada Lovelace    London
    Query Should Return    SELECT city FROM customer WHERE name = 'Ada Lovelace'    London
    Table Should Have Rows    customer    1

Move And Delete Are Stored
    [Documentation]    A move changes the city, deleted customers are gone.
    Create Customer    Ada Lovelace    London
    Create Customer    Alan Turing    Manchester
    Change City    Ada Lovelace    Munich
    Query Should Return    SELECT city FROM customer WHERE name = 'Ada Lovelace'    Munich
    Delete Customer    Alan Turing
    Table Should Have Rows    customer    1
