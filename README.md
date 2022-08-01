# polaris-behealthy

**polaris-behealthy** is a BDD Toolkit for Polaris Services to ensure our integrations are healthy.

**polaris-behealthy** is a wrapper around [behave](https://behave.readthedocs.io/en/latest/), the Python library that lets us write tests in natural language and use Behaviour Driven Development.

With **polaris-behealthy** we can write tests like

```
Given I am a Clinician using SEND Entry
When I submit a NEWS2 Observation Set
Then a PDF is generated containing the data submitted
```

For a full list of tests and descriptions of what they do, see [The Table Of Contents](./docs/toc.md).

## Maintainers
The Polaris platform was created by Sensyne Health Ltd., and has now been made open-source. As a result, some of the
instructions, setup and configuration will no longer be relevant to third party contributors. For example, some of
the libraries used may not be publicly available, or docker images may not be accessible externally. In addition, 
CICD pipelines may no longer function.

For now, Sensyne Health Ltd. and its employees are the maintainers of this repository.


## Installation

**polaris-behealthy** requires Python 3.9.

```
poetry install -v
```

# Run The Tests

To run the tests, set environment variable `ENVIRONMENT` to the environment the tests should run against 
(e.g. "dev", "usdev", or "staging"):

```
$ ENVIRONMENT="dev" behave
Feature: Observation Sets # ../observations.feature:1

    Scenario: Check For PDF                      # ../observations.feature:3
        Given I am a Clinician using SEND Entry  # clinicians.py:4 0.000s
        When I submit a NEWS2 Observation Set         # observations.py:4 0.000s
        Then a PDF is generated                  # clinicians.py:9 0.000s

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
3 steps passed, 0 failed, 0 skipped, 0 undefined
Took 0m0.000s
```

Note that there is no `.` after the `behave` command, which is a common gotcha. If you execute `behave .` then you'll have little joy.

To run an individual Feature file, for example the EPR Adapter Failed Requests Scenario(s), from the command line execute:

```
$ behave -i failed_requests

```

To run and see any `print` statements you may have added to debug, execute:

```
$ behave --no-capture
```

To run specific test(s), decorate Scenario(s) with tags such as @sms and execute:

```
$ behave --tags=sms
```

# Write The Tests

Writing end-to-end Acceptance Tests for your Feature will get easier and easier the more people write them because the toolkit at our disposal will grow. Please follow the protocol below, and look at existing feature files and steps to get a better understanding.

- Your first task is to create a Feature file in `./features`, unless there is on there already that encapsulates your Scenario nicely. Let's assume it's a new file called `foobar.feature`.

- Next declare the Feature title at the top of the file, and then a 4-space indented description. Leave a blank line, then declare the Scenario name. All of these need to be formatted correctly, as these will be parsed to add your test to the Table Of Contents.

- Now you need to write your Steps. All Steps are prefixed by `behave` key words: **Given**, **And**, **Then**, **When**. This is how `behave` knows what Python function to map the Step to. These are generally in 3 parts.

  1. Declare the setup Steps you need, e.g. create a clinician. These Steps are likely to exist already, so read other test cases first. The more tests people write, the more likely you can breeze through the setup.
  2. Declare the Step that executes the action you want to test the side effects for, e.g create an Encounter. If these don't exist, you'll likely need to add a new API Client or a new API to an existing one from `she-http-clients` to achieve your goal.
  3. Declare the Step that does your assertion. For this you'll might want to use `assert_stops_raising` to wait for async/background jobs to complete.

```
Feature: FooBar

    Description here...

    Scenario: Check that Bar is created when I Foo

        Steps here...
```

- Now you should have your end-to-end Scenario written out in Steps. For each one that does not already exist in `./features/steps`, this is where you need to start writing some Python. Try and namespace your Step (i.e. choose or create the most suitably named module) such that other readers can quickly guess where to find your Step definitions.

- Run your test!

```
$ behave -i foobar
```

- Once happy, create a PR.

# Debug The Tests

> :warning: Note: the `behave` framework does funny things to log outputs. You may need to add a newline after your logging messages so that they appear in the console; `behave` likes to remove lines for its own output. To see all available logging, you should also make sure you use the behave arguments `--logging-level DEBUG --no-capture --no-logcapture`.

When a test case fails it can be particularly difficult to figure and why, and this is because these are end-to-end tests which span any number of the platform services, crossing message queues, interacting with databases, file systems and caches.

Why do tests fail? These are the most common reasons, and feel free to add to this list.

- A breaking code change in any of the Polaris services or dependencies
- Infrastructure failure, e.g. Postgres, Rabbit, Neo, Redis, Nginx
- A bug, race condition or flaky test within BeHealthy

How do tests fail?

- [Assert stops raising](behealthy/utils/assertions.py#L4)... raises!
- An Exception in BeHealthy
- An Exception in Polaris

When one does fail, and especially if you're not familiar with the Scenario, it can be hard to know where to start. So please do read this how-to guide before you begin to tear your hair out.

### Jenkins Console Output

Within this rather daunting long page of messy stdout, some giant clues have be left for you.

- All env variables are printed out at the top of the page
- You can see exactly what Step in your test failed
- When any step fails, the request ID used in the HTTP requests for that step is dumped to the page

```
Captured logging:
      WARNING:behealthy:step failed: I submit a NEWS2 Observation Set with request ID Check-Observation-Set-is-Scored-I-submit-an-Observation-Set-2019-05-19T09:59:37251023
```

- When any Step fails due to an `AssertionError`, the last assertion is dumped to the page. Search the page for "most recent assertion".
- When a Step fails due to an `Exception` the stack trace is (normally) dumped to the page.
- After a Scenario fails, clues are dumped to the Page. These are the objects created during the test run so you can inspect them. Search the Page for "showing all clues collected during scenario execution". Each clue is tied to a Step by the Step's prose (the string we decorate the Step with).

### Run The Test Locally!

The easiest way to debug is to run the tests locally. See "Run The Tests" above.

```
$ behave --no-capture <your-feature-file(s)>
```

### Platform Logs

Once you have your Request ID (in theory) that can be used to harvest relevant logs.

It's certainly best to have a clue of some sorts, rather than just scrolling through them, e.g. an expected log line.

### RabbitMQ

Tests can fail if:

- Rabbit is backed up and takes too long to process your messages, causing **assert_stops_raising** to raise.
- Your message ends up on the **error queue**.

To rule this out, see instructions [here](https://sensynehealth.atlassian.net/wiki/spaces/SENS/pages/25985044/Infrastructure+Tooling) to view the Dev RabbitMQ instance.

For the first, all queues should have nothing in them. If there are <10 messages, you're probably fine. If a queue (other than the error queue) has hundreds, then something is wrong.

Regarding the error queue, you can fetch the last messages and see if anything from your test is there (first look at the "clues" in the Jenkins console to get the IDs of patients, encounters, obs sets etc. etc.).
