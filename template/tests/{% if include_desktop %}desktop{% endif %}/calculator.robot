*** Settings ***
Documentation       Hello world for desktop: calculates in the Windows calculator. Runs only with the profile
...                 "desktop": uv run robotcode -p desktop robot (do not use mouse and keyboard meanwhile)
Resource            ${EXECDIR}/resources/tasks/desktop_tasks.resource
Resource            ${EXECDIR}/resources/assertions/desktop_assertions.resource
Test Setup          Start Calculator
Test Teardown       Close Calculator
Test Tags           desktop    hello-world    requires-desktop


*** Test Cases ***
Calculator Adds
    [Documentation]    12 + 30 is 42.
    Calculate    12+30
    Program Element Should Show Text    ${calculator.result}    42

Calculator Multiplies
    [Documentation]    6 times 7 is 42.
    Calculate    6*7
    Program Element Should Show Text    ${calculator.result}    42
