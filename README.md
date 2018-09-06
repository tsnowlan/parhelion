When working with sensitive data, it can be hard to test code without using the production
environment. This is Not Good. If you're lucky, the input data you're working with is well
defined, so you can generate test data without much effort. However, if you're working with
complex data, or a third-party service, you might not have access to that information. The
goal of Parhelion is to feed real data into the parser and create a general model based on
that. With that model, it can then generate new test data as needed.

Currently only supports XML input because that is what I need right now. Ideally, the framework
can be extended to any data format.
