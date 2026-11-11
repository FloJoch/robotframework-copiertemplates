*** Settings ***
Documentation       Technical helper keywords of the basics (environments, credentials, CryptoLibrary).
...                 Tagged "interaction": used by tasks and assertions, never directly in tests.
Resource            ${EXECDIR}/resources/main.resource
Keyword Tags        interaction


*** Keywords ***
Read Login For Environment
    [Documentation]    Returns the credentials (username, password) of the given environment.
    [Arguments]    ${environment}
    RETURN    ${LOGINS}[${environment}]

Hide Value In Log
    [Documentation]    Makes sure the value only appears as *** in log and report.
    [Arguments]    ${value}
    Conceal Text In Logs    ${value}
