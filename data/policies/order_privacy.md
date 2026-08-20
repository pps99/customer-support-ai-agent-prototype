# Order Privacy and Customer Verification Policy

## Protected Order Information

Order status, tracking information, shipping address, purchase history, payment details, and
other order-specific information are considered customer information.

The support agent must not disclose order-specific information unless the requester has been
verified.

## Verification Requirements

For this prototype, verification requires both:

- a valid order number
- the email address associated with that order

Both values must match the stored order record.

## Verification Failure

If the order number does not exist or the email address does not match, the support agent
must not reveal:

- whether the order exists
- the customer's name
- shipping details
- tracking details
- order contents
- payment information

The agent should respond with a neutral message stating that the order could not be verified.

## Missing Information

If the customer provides only an order number or only an email address, the agent should ask
for the missing information rather than guessing.

## Sensitive Changes

The AI agent must not automatically perform sensitive account or delivery changes, including:

- changing the shipping address
- changing the email associated with an order
- changing payment information
- transferring an order to another customer

These requests require human review.