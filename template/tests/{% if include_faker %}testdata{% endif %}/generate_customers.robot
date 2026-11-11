*** Settings ***
Documentation       Hello world for test data: generate fake customers with the FakerLibrary.
Resource            ${EXECDIR}/resources/tasks/faker_tasks.resource
Resource            ${EXECDIR}/resources/assertions/faker_assertions.resource
Test Tags           testdata    hello-world


*** Test Cases ***
Generated Customer Is Complete
    [Documentation]    A generated customer has all details and a valid e-mail address.
    ${customer}    Generate Random Customer
    All Fields Should Be Filled    ${customer}
    Email Address Should Be Valid    ${customer}[email]

Several Customers Have Different Email Addresses
    [Documentation]    Five generated customers have five different e-mail addresses.
    ${customers}    Generate Random Customers    5
    ${addresses}    Collect Email Addresses    ${customers}
    Values Should Be Unique    ${addresses}
