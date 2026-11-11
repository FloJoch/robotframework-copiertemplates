*** Settings ***
Documentation       Accessibility of pages behind a login (demo shop saucedemo.com).
...                 After login, the product overview and the cart are checked and reported.
Resource            ${EXECDIR}/resources/tasks/accessibility_tasks.resource
Resource            ${EXECDIR}/resources/assertions/accessibility_assertions.resource
Test Setup          Start Audit Browser
Test Teardown       Stop Audit Browser
Test Tags           accessibility    login


*** Test Cases ***
Product Overview After Login Is Accessible
    [Documentation]    The product overview after login has no serious violations.
    Log In For Audit
    ${violations}    Audit Accessibility Of Current Page
    Page Should Have No Serious Violations    ${violations}

Cart After Login Is Accessible
    [Documentation]    The cart after login has no serious violations.
    Log In For Audit
    Open Cart For Audit
    ${violations}    Audit Accessibility Of Current Page
    Page Should Have No Serious Violations    ${violations}
