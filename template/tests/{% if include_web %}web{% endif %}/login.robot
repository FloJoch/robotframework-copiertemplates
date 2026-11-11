*** Settings ***
Documentation       Hello world for web: login in the demo shop saucedemo.com.
Resource            ${EXECDIR}/resources/tasks/web_tasks.resource
Resource            ${EXECDIR}/resources/assertions/web_assertions.resource
Test Setup          Start Browser
Test Teardown       Stop Browser
Test Tags           web    hello-world


*** Test Cases ***
Login With Valid Credentials Shows The Products
    [Documentation]    With the credentials of the environment the product overview appears after login.
    Open Login Page
    Log In
    Element Should Show Text    ${MAIN_TITLE}    Products
    Number Of Elements Should Be    ${MAIN_PRODUCTS}    6

Login With Wrong Password Is Rejected
    [Documentation]    With a wrong password an error message appears.
    Open Login Page
    Log In    standard_user    wrong-password
    Element Text Should Include    ${LOGIN_ERROR_MESSAGE}    do not match
