*** Settings ***
Documentation       Hello world for web: cart and logout in the demo shop saucedemo.com.
Resource            ${EXECDIR}/resources/tasks/web_tasks.resource
Resource            ${EXECDIR}/resources/assertions/web_assertions.resource
Test Setup          Start Browser
Test Teardown       Stop Browser
Test Tags           web    hello-world


*** Test Cases ***
Product Lands In The Cart
    [Documentation]    A product appears in the cart after adding it.
    Open Login Page
    Log In
    Add Product To Cart    sauce-labs-backpack
    Element Should Show Text    ${MAIN_CART_BADGE}    1
    Open Cart
    Element Should Show Text    ${CART_ITEM_NAMES}    Sauce Labs Backpack

Logout Leads To The Login Page
    [Documentation]    After logout the login page is shown again.
    Open Login Page
    Log In
    Log Out
    Element Should Be Shown    ${LOGIN_BUTTON}
