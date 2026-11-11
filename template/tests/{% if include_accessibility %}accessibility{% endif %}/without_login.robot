*** Settings ***
Documentation       Accessibility of public pages (no login), data-driven: every row is one page.
...                 A report is written automatically for every page to results/accessibility/.
Resource            ${EXECDIR}/resources/tasks/accessibility_tasks.resource
Resource            ${EXECDIR}/resources/assertions/accessibility_assertions.resource
Suite Setup         Start Audit Browser
Suite Teardown      Stop Audit Browser
Test Template       Page Is Accessible
Test Tags           accessibility    hello-world


*** Test Cases ***    ADDRESS
Example Page          https://example.com
Wikipedia Start Page  https://www.wikipedia.org


*** Keywords ***
Page Is Accessible
    [Documentation]    Checks a page, writes the report and fails on serious violations.
    [Arguments]    ${address}
    ${violations}    Audit Accessibility Of Page    ${address}
    Page Should Have No Serious Violations    ${violations}
