*** Settings ***
Documentation       Actions of the basics - these keywords are used in tests.
Resource            ${EXECDIR}/resources/interactions/core_interactions.resource


*** Keywords ***
Read Credentials Of Environment
    [Documentation]    Gets user and password of the environment (default: the active environment),
    ...    hides the password in the log and returns the credentials.
    [Arguments]    ${environment}=${ENV}
    ${login}    Read Login For Environment    ${environment}
    Hide Value In Log    ${login}[password]
    RETURN    ${login}
