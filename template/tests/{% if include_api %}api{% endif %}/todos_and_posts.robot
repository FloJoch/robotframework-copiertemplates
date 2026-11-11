*** Settings ***
Documentation       Hello world for APIs: fetch todos and create a post (open test API).
Resource            ${EXECDIR}/resources/tasks/api_tasks.resource
Resource            ${EXECDIR}/resources/assertions/api_assertions.resource
Test Tags           api    hello-world


*** Test Cases ***
Todo One Can Be Fetched
    [Documentation]    The todo with the number 1 can be fetched.
    ${response}    Fetch Todo    1
    Status Code Should Be    ${response}    200
    Response Field Should Be    ${response}    id    1

Todos Of A User Are Filtered
    [Documentation]    User 1 has todos.
    ${response}    Fetch Todos Of User    1
    Status Code Should Be    ${response}    200
    Response Should Have At Least Entries    ${response}    1

New Post Is Created
    [Documentation]    A new post is accepted and returned with its title.
    ${response}    Create Post    Hello    My first post
    Status Code Should Be    ${response}    201
    Response Field Should Be    ${response}    title    Hello
