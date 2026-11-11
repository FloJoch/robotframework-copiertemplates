*** Settings ***
Documentation       Generic checks included in every project - these keywords are used in tests.
Resource            ${EXECDIR}/resources/interactions/core_interactions.resource


*** Keywords ***
Value Should Be Filled
    [Documentation]    Checks that a value is not empty.
    [Arguments]    ${value}    ${message}=The value is empty
    ${text}    Convert To String    ${value}
    Should Not Be Empty    ${text}    ${message}

Value Should Equal
    [Documentation]    Checks that a value is exactly the expected value.
    [Arguments]    ${value}    ${expected}
    Should Be Equal As Strings    ${value}    ${expected}

Text Should Include
    [Documentation]    Checks that a text includes the expected part.
    [Arguments]    ${text}    ${expected}
    Should Contain    ${text}    ${expected}

Credentials Should Be Complete
    [Documentation]    Checks that username and password are set.
    [Arguments]    ${login}
    Value Should Be Filled    ${login}[username]    Username is missing in main.resource
    Value Should Be Filled    ${login}[password]    Password is missing in main.resource
