# [Functional, Action, Sequence: 3 Diagram Types for Multi-Dimensional Software Modelling](https://dev.to/eugene-zimin/functional-action-sequence-3-diagram-types-for-multi-dimensional-software-modeling-3a50)
When developing a new software system, diagrams are invaluable tools for documenting the design and architecture. Three diagram types that are especially useful for clear communication and mapping out software structure are functional diagrams, sequential diagrams, and action diagrams. In this article, I will provide an overview of each of these diagram types, explain what kind of information they are best for conveying, and provide examples to demonstrate how to put together functional, sequential, and action diagrams for a software project. Whether we're a software architect creating new design docs or a developer trying to understand existing systems, having a grasp of these three diagramming techniques can improve understanding and communication around complex software systems. Read on to learn how functional, sequential, and action diagrams can help us visualize and document software designs.

## Different Angles - One System

Functional, action, and sequence diagrams serve distinct yet complementary purposes in software design. Each diagram type looks at the system from a different angle, providing unique perspectives that together contribute to a comprehensive understanding.

Functional diagrams offer a static, structural perspective by breaking down the software into functional components and displaying their logical organization and relationships. This static view focuses on what elements make up the system and how they architecturally connect.

In contrast, action and sequence diagrams take a dynamic, behavioral view of the runtime aspects of the system. Action diagrams display the procedural flow through key processes while sequence diagrams reveal the detailed object interactions during execution. These dynamics views center on how the system operates.

Using both static and dynamic views in combination enables tracing from architecture to implementation. The functional diagrams provide the scaffolding to be fleshed out by behavioral logic in action and sequence diagrams. The multiple angles combine to tell a complete story.

In other words, functional and action diagrams give high-level overviews of the system, simplifying complexity with abstraction. Meanwhile, sequence diagrams offer a detailed, tactical focus ideal for drilling into specifics. These complementary zoomed out and zoomed in perspectives are invaluable.

By leveraging all three standard diagram types, software systems can be thoroughly visualized from multiple standpoints, enabling superior comprehension, communication and documentation.

## Understanding Action Diagrams

Action diagrams or flowcharts are a simple yet powerful way to visualize the flow of actions in a software system. They depict how a set of actions are sequenced together to accomplish a specific task or workflow from different points of view - from user prospective experience, or describe from the architecture point of view. Speaking much generic, they are graphical representations of the steps and decision points in a process.

Unlike sequence diagrams, which focus on object interactions, action diagrams illustrate the flow of procedural logic through a process. That is very important thing, explaining the difference between two of them. In action diagrams we usually do not review such level of technical details like application objects interactions, because even though it gives us a very comprehensive view, it makes it much harder to abstract the general logic of the software and lose the line.

The steps are arranged sequentially from top to bottom, guiding the reader through the flow of the actions. Action diagrams typically contain the following elements:

- **Actions** - These are represented in boxes or circles and use active verbs or short phrases to describe steps. For example, "Validate Form", "Call Payment API", "Send Notification Email".
- **Connections** - Arrows connect the actions to indicate flow. Conditional logic can be shown using branches or decision nodes.
- **Swimlanes** - Horizontal swimlanes can group related actions for different components or actors.
- **Annotations** - Additional text can explain inputs, outputs, etc. 

Some key benefits of using action diagrams include:
#### Clarifying complex logic flows at a high level
Action diagrams allow us to understand a complex workflow or business process at a high level before diving into the implementation details. The sequential flow and branching logic help clarify what steps occur and in what order.
#### Illustrating different branches in conditional logic
Complex conditional logic is common in real-world software workflows. Action diagrams enable us to visualize different branches that occur based on conditions or decisions in the flow. The diagram makes it easy to see how the happy path and edge cases are handled.
#### Visualizing steps for workflows, user stories, or test cases
Action diagrams are useful for documenting workflows tied to user stories or requirements. They provide a visualization of the steps to be coded (see the reference to the high level logic description) . Action diagrams can also aid in test case planning since they illustrate the key flows to be tested.
#### Serve as a base for lower-level sequence diagrams
The high-level action diagram can be a starting point for drilling down into more detailed sequence diagrams. The sequence diagrams can focus on expanding specific actions from the action diagram into the object interactions needed to implement them. Using the action diagram as a guide, multiple complementary sequence diagrams can be created to cover all the steps
#### Improving documentation through diagrams
Diagrams are much more effective at conveying complexity than pure text. Action diagrams ensure the documentation captures the logic visually, making it easier for new team members to understand.

Let's look at an example action diagram for a user login/signup flow:

![Flowchart](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/7pmbwm8o9rlgq2y2957x.png)

This diagram shows the sequential steps the system will walk through to complete the use case of a user signing up for an account. Key flows like handling invalid input are called out. 

Action diagrams help summarize complex workflows at a high level while still illustrating logical flow, branches, conditions and edge cases. They provide an intuitive way to understand how a software system accomplishes its goals. Developers can rely on the action diagram as a base or skeleton, and fill in the implementation details in granular sequence diagrams for each step. This helps ensure the lower-level diagrams trace back and support the overall workflow represented in the action diagram.

### Stepping in With Flowcharts

Here are few some simple steps to follow with a good action diagram. 
#### Identify the Process
Start by clearly defining the process or workflow which is needed to be diagramed. We need to keep in memory, that flowcharts are called so because the describe flow in system design, where every flow has begin and end points. That is why it is very important to identify them and describe them first. 
For example, if we are diagramming the process for a customer trying to login to the web portal, the start point could be the customer loading the initial page or trying to reach out any page in the web portal and get redirected into the login page. As the end point there could be considered a showing to the user his profile page or some other default page.
#### Determine the Steps
Break down the process into individual steps. Each step should represent a single action or decision point. For instance, in the user login process, steps might include "Display form", "Fill in the form", etc.
#### Use Standard Symbols
Always try to utilize standard flowchart symbols to represent different elements of the process. For example, use rectangles for actions, diamonds for decision points, and arrows for the flow direction. This standardization helps in making the diagram universally understandable. It is possible to use UML as a design standard.
#### Arrange the Steps Sequentially
Place the steps in the order they occur, from top to bottom or left to right. Ensure that the flow is logical and easy to follow. We should always ask ourselves - if we perform this action, what should happen next?
#### Label the Steps
Clearly label each step with a brief description of the action or decision. Use concise and clear language. For example, instead of just "Login," label the step as "Enter Login Information."
#### Indicate Decision Points
Use decision symbols to represent points in the process where a choice must be made. Label each outgoing arrow from a decision point to indicate the criteria for each path. For example, at a decision point like "User exists?" the outgoing arrows could be labeled "Yes, proceed with login" and "No, register user first".
#### Review for Completeness and Clarity
Once the diagram is complete, review it to ensure that it accurately represents the process and is easy to understand. Make any necessary adjustments. This might involve rearranging steps, adding missing steps, or clarifying labels.

## Diving Into Functional (Block) Diagrams
Functional diagrams, also known as block diagrams, are a valuable type of diagram used in software design. They illustrate the high-level functions and interactions in a system by breaking down the overall system into its main functional components and showing how they connect and share data.

It might be easier to understand them comparing their place in system design and architecture with other types of diagrams.

Unlike sequence diagrams or action diagrams (flowcharts) which focus on the step-by-step logic, functional diagrams aim to provide a bird's eye view of the system architecture. The functional elements that make up the overall system are represented as blocks or bubbles on the diagram.

Sequence diagrams display detailed interactions between objects and the order of messages passed between them. Flowcharts illustrate the tactical progression of steps through a process.

In contrast, functional diagrams zooms out to look at the system from a wider lens. Functional diagrams are focused on the structural decomposition of the system into major building blocks. So instead of drilling down into the tactical flow, they partition the system into high-level functional components.

These functional components are depicted as abstract blocks, not necessarily tied to specific classes or objects. The blocks represent logical groupings by broad areas of functionality. For example, there may be a block for the UI functions, the business logic functions, the persistence functions, and so on.

The goal is to break down the overall system into major functional pieces, show how they connect together, and provide a conceptual overview. Functional diagrams help crystallize the architectural vision and big picture before diving into implementation details with other diagram types.

### Why to Use Functional Diagrams?

Functional diagrams provide valuable high-level visualization of a system's architecture and design. Some specific benefits include:
#### Logical overview of system architecture
Functional diagrams allow us to logically group major system capabilities into modular blocks that abstractly represent the overall structure. This bird's eye view establishes the architectural vision.
#### Illustrating relationships between elements
By connecting functional blocks with annotated arrows, functional diagrams clearly display the relationships and dependencies between components. This reveals how the pieces interact at a high level.
#### Capturing architectural details
Functional diagrams permit capturing a degree of technical details related to the architecture. For example, labeled arrows can represent messaging protocols used between components or specific APIs exposed by a block.
#### Data flows
The connections between blocks can indicate data flows between functional elements, highlighting where information is produced, consumed and transformed.
#### Complementing UML
While UML provides implementation specifics, functional diagrams effectively communicate high-level system design intent and architecture. The diagrams are complementary.
#### Communication
Functional diagrams create a common visual language for technical and non-technical stakeholders to understand system organization and interactions.
#### Foundation for other models
Functional diagrams provide the 20,000 foot view of the landscape to ground more detailed models like UML, flowcharts, etc.

By leveraging functional diagrams, architects and designers can effectively model and communicate key architectural aspects and relationships to set the stage for detailed implementation.

### Preparing Functional (Block) Diagrams

When determining what functional blocks to include on a functional diagram, it is important to use nouns to label the blocks, not verbs. For example, correct block names would be "Inventory System", "Payment Gateway", "User Profile", not "Validate User", "Process Order", "Verify Payment".

Functional diagrams contain the following key elements:

- **Blocks** - Represent major functions or components of the system. Blocks can be systems, subsystems, classes, services, etc.
- **Connections** - Arrows between blocks show how they interact and communicate with each other.
- **Annotations** - Additional text can label connections to explain the nature of interactions.

Example of the functional diagram is below.

![functional block diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/nl0vdogefxbjtp0baqwf.png)

It is easy to begin with diagraming while architecting a system or application, following simple rules below:
#### Start with High-Level Functions
Begin by identifying the major functionality of the system. These should represent the core capabilities or services provided by the system. For example, in an e-commerce platform, high-level functionality might include Product Catalog, Shopping Cart, Payment Processing, and Order Fulfillment. This step sets the foundation for the functional diagram by establishing the key areas of functionality within the system.
#### Break Down Complex Functions
If the chosen functionality is too complex, consider breaking it down into smaller, more manageable sub-functionalities. This helps in maintaining clarity and focus in the diagram. For instance, the Payment Processing function could be broken down into sub-functions like Credit Card Validation, Payment Authorization, and Payment Confirmation. This granularity ensures that each block in the diagram is focused and understandable.
#### Use Consistent Labeling
Ensure that all blocks are labeled consistently, using nouns that clearly describe the functionality or component. It is recommended even though not mandatory to avoid using technical jargon that might be confusing to non-technical stakeholders. For example, use clear and descriptive labels like "User Authentication" instead of vague or technical terms like "Auth Module". In all cases consistent labeling helps in making the diagram more accessible and easier to understand for all stakeholders.
#### Indicate Data Flow
Use arrows to show the flow of data or control between different functional components. This helps in understanding how information is processed and transferred within the system. For example, an arrow from the Shopping Cart function to the Payment Processing function indicates that the shopping cart details are passed to the payment process for transaction completion. Clearly indicating data flow provides insight into the interactions between different functions and how they work together to achieve the system's objectives.
#### Validate with Stakeholders
Regularly review the diagram with stakeholders to ensure that it accurately represents their understanding of the system. This is crucial for aligning the technical architecture with business requirements. Engaging stakeholders in the validation process ensures that their perspectives and needs are reflected in the diagram, leading to a more accurate and relevant representation of the system.

## Modelling Detailed Logic with Sequence Diagrams

Sequence diagrams are a third important type of diagram used when designing software systems. While functional and action diagrams provide high-level overviews, sequence diagrams drill down to illustrate detailed logic and object interactions.

Sequence diagrams work by representing software objects as vertical boxes or "lifelines" over a timeline. Messages passed between objects are shown sequentially down the diagram to visualize the procedural flow.

Sequence diagrams are an essential tool for visualizing detailed software logic and object interactions. The granular focus of sequence diagrams allows us to zoom in on the flow for a distinct use case rather than trying to capture all flows in one diagram. This makes them ideal for detailing individual stories or features.

The core purpose of sequence diagrams is showing how objects collaborate and exchange data during a scenario, which matches nicely to modeling story requirements. The chronological visualization provided by sequence diagrams also aligns well with displaying the progression of steps through a workflow or user path.

Sequence diagrams work best for reasonably complex scenarios with around 5-15 steps. This level of abstraction is in the ideal sweet spot for capturing coherent stories or workflows, neither too high-level nor too detailed.

The objects and messages also correspond well to classes and methods needed to implement the scenario, providing traceability from requirements to code. Sequence diagrams allow clear visual communication of detailed logic to explain stories to stakeholders and developers.

The focused scope, object interaction modeling, logical sequential flows, ideal abstraction level, traceability, and communication strengths make sequence diagrams a great tool specifically for breaking down and displaying software scenarios at the granularity of user stories. The techniques are very complementary.

Key elements in a sequence diagram include:

- **Objects** - Shown as lifelines labeled with class names or components
- **Messages** - Arrows between lifelines indicate messages communicating data
- **Time sequence** - Messages are ordered sequentially down diagram
- **Returns** - Dotted arrows back to caller lifeline for return messages
- **Controls and conditions** - Text notations for loops, conditionals, etc

Some benefits of using sequence diagrams:

- Reveal detailed logic and execution flow through use case
- Visualize complex object collaborations and data flows
- Model software logic for documentation and testing
- Complement higher-level action diagrams

Sequence diagrams are essential for understanding and communicating how objects interact to implement software behavior and use cases. They provide a dynamic view of detailed system execution.

In the next sections we'll walk through an example to see how to build a sequence diagram.
### Sequence Diagram Example

Let's look at a simple example sequence diagram for a user login flow:

![sequence diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/hfl0hx6r9felybvosm26.png)

The diagram would start with two lifelines - one labeled "User" and one labeled "LoginController".

The first arrow goes from User to LoginController labeled `submitLogin(username, password)` indicating the user sends login credentials.

LoginController sends an arrow to the Database lifeline with the message `query(username)` to look up the user.

The Database returns user data back to LoginController.

LoginController sends a message to itself `validate(user, password)` to validate against the retrieved data.

If valid, LoginController sends `loginSuccess(user)` back to User.

If invalid, it sends `loginFailed(error)` back to User instead.

That covers the basic flow. Additional logic like forgotten password handling could also be added.

The key is using object lifelines and chronological messages to reveal the step-by-step interactions. This brings low-level logic to life visually.
### Creating Sequence Diagrams

Here are some steps to follow when creating a sequence diagram:

1. Identify the scenario or use case to diagram. For example, this could be a user signup flow, payment processing, order fulfillment, etc. Focus on a specific workflow.
2. Determine the key objects involved in the scenario. The nouns in the use case often provide clues. For a user signup flow, the objects might be `User`, `SignupController`, `AuthenticationService`, etc. These objects become the vertical lifelines.
3. Map out the major steps sequentially from top to bottom. Focus on the overarching logical flow first before details. For example, the signup steps could be: Load registration form -> Submit credentials -> Validate inputs -> Create account -> Send welcome email.
4. Represent actions as messages passed between object lifelines. Use clear imperative phrases for message names like `submitRegistration(user)`, `validateCredentials(username, password)`.
5. Include returns back to the calling object for response messages. For example, after calling `validateCredentials()` the `AuthenticationService` would return either `credentialsValid()` or `credentialsInvalid()`.
6. Number or label messages if needed to indicate ordering for complex flows with conditionals or loops. This clarifies sequence.
7. Use swimlanes to optionally group related lifelines, such as putting all UI objects in one lane and service objects in another.
8. Refine the diagram iteratively, adding more steps or reordering as logic is clarified. Diagrams evolve incrementally.
9. Review the completed diagram to validate the end-to-end flow makes sense. Update as needed.

Following these tips will allow us to leverage sequence diagrams to bring complex software executions to life on the page. The step-by-step visualization enables clearer communication and shared understanding.

## Bringing the Diagrams Together

Functional, action, and sequence diagrams all play important roles in documenting software systems, but provide unique perspectives. Understanding how the diagrams complement each other is key.

### Static vs Dynamic Views

Functional diagrams provide a **static structural view** by breaking the system into functional components. The diagrams display logical organization and relationships between elements.

Action and sequence diagrams offer **dynamic behavioral views** of the system. Action diagrams illustrate procedural flow through a process. Sequence diagrams reveal detailed object interactions.

### High-level vs Detailed Focus

Functional and action diagrams give a **high-level overview** of the system architecture and workflows. They simplify complex systems with an abstracted view.

Sequence diagrams take a **detailed focus** to unfold specific use cases and object collaborations during execution. The diagrams get tactical.

### Architectural vs Implementation Views

Functional diagrams align closely to **architectural modeling** to design the overarching system structure. They can inform high-level technical decisions.

Action and sequence diagrams tend towards **implementation modeling** to plan detailed logic, steps, and object interactions during coding.

### Traceability

When created together, the diagrams form crucial traceability between architectural design and implementation specifics. The perspectives combine to tell a complete story.

By leveraging these diagram types together, software systems can be thoroughly visualized to improve understanding and communication.