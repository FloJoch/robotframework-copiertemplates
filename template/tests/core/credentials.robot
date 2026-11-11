*** Settings ***
Documentation       Hello world of the basics: credentials per environment and CryptoLibrary.
Resource            ${EXECDIR}/resources/tasks/core_tasks.resource
Resource            ${EXECDIR}/resources/assertions/core_assertions.resource
Test Tags           core    hello-world


*** Test Cases ***
Credentials Of Active Environment Are Set
    [Documentation]    User and password are set for the active environment (dev, test, prod).
    ${login}    Read Credentials Of Environment
    Credentials Should Be Complete    ${login}

Credentials Of Test Environment Are Set
    [Documentation]    The credentials of another environment can be read on purpose, too.
    ${login}    Read Credentials Of Environment    test
    Credentials Should Be Complete    ${login}
