# modelChecker

modelChecker is a tool written for Autodesk Maya to sanity check digital polygon models for production. It aims to be as unopinionated as possible, It gives you concise error reporting, and let's you select your error nodes easily.

![modelChecker](https://i.imgur.com/1PQr1S5.jpg)

## Setup

Place the modelChecker files in your Maya scripts directory and create a python shell button with the following code:

```python
from modelChecker_UI import modelCheckerUI

modelCheckerUI.show_UI()
```

## Usage

There are three ways to run the checks.

1. If you have objects selected the checks will run on the current selection.
2. A hierachy by declaring a top node in the UI.
3. If you have an empty selection and no top node is declared the checks will run on the entire scene.

## Authors

- [**Jakob Kousholt**](https://www.linkedin.com/in/jakejk/) - Software Engineer / Freelance Creature Modeler
- [**Niels Peter Kaagaard**](https://www.linkedin.com/in/niels-peter-kaagaard-146b8a13) - Senior Modeler at Weta Digital

## Support & Feedback

For any bugs, errors, and requests feel free to reach out to [Jake](mailto:jakobjk@gmail.com)

If you want to support us, feel free to "buy" the modelChecker from [Gumroad](https://jakejk.gumroad.com/l/htZYj).

## License

modelChecker is licensed under the [MIT](https://rem.mit-license.org/) License.
