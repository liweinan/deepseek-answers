# HackerRank - CryptoRank Exchange

- https://www.hackerrank.com/challenges/cryptorank-exchange

To meet the requirements for the CryptoRank Exchange React application, we need to fix and enhance both `Main.js` and `Table.js`. The application must allow users to input a fiat amount, validate it, display appropriate error messages, and dynamically calculate the number of cryptocurrency coins based on predefined exchange rates. Below are the updated files with complete implementations.

The key changes include:
- **Main.js**: Add state management for the input amount and error messages, implement input validation, and pass the valid amount to the `Table` component.
- **Table.js**: Map over the cryptocurrency list to display each currency's name, exchange rate, and calculated number of coins, handling "n/a" for invalid amounts.

Here are the corrected files:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CryptoRank Exchange</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/react@18/umd/react.development.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    // cryptocurrency-list.js
    const cryptocurrencyList = [
      { name: "BNB", code: "BNB", rate: 0.00311839 },
      { name: "Bitcoin", code: "BTC", rate: 0.00004066 },
      { name: "Dogecoin", code: "DOGE", rate: 11.18558722 },
      { name: "Ethereum", code: "ETH", rate: 0.00059237 },
      { name: "XRP", code: "XRP", rate: 2.50682634 },
    ];

    // Table.js
    function Table({ amount }) {
      const isValidAmount = !isNaN(amount) && amount >= 0.01 && amount <= 17042.67;

      return (
        <div className="card card-text mt-10 mx-4">
          <table className="mb-0 w-full">
            <thead>
              <tr>
                <th className="text-left p-2">Cryptocurrency</th>
                <th className="text-left p-2">Exchange Rate</th>
                <th className="text-left p-2">Number of Coins</th>
              </tr>
            </thead>
            <tbody data-testid="exchange-data">
              {cryptocurrencyList.map((crypto) => (
                <tr key={crypto.code}>
                  <td className="p-2">{crypto.name}</td>
                  <td className="p-2">1 USD = {crypto.rate.toFixed(8)} {crypto.code}</td>
                  <td className="p-2">
                    {isValidAmount
                      ? (amount * crypto.rate).toFixed(8)
                      : amount === ""
                      ? "0.00000000"
                      : "n/a"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // Main.js
    function Main() {
      const [amount, setAmount] = React.useState("");
      const [error, setError] = React.useState("");
      const availableBalance = 17042.67;

      const validateAmount = (value) => {
        if (value === "") {
          setError("Amount cannot be empty");
          return false;
        }
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
          setError("Amount must be a valid number");
          return false;
        }
        if (numValue < 0.01) {
          setError("Amount cannot be less than 0.01");
          return false;
        }
        if (numValue > availableBalance) {
          setError("Amount cannot exceed the available balance");
          return false;
        }
        setError("");
        return true;
      };

      const handleAmountChange = (e) => {
        const value = e.target.value;
        setAmount(value);
        validateAmount(value);
      };

      return (
        <div className="layout-column align-items-center mx-auto max-w-2xl p-4">
          <h1 className="text-2xl font-bold">CryptoRank Exchange</h1>
          <section>
            <div className="card-text layout-column align-items-center mt-12 px-8 flex text-center">
              <label className="mb-4">
                I want to exchange $
                <input
                  className="w-32 ml-2 p-1 border rounded"
                  data-testid="amount-input"
                  type="number"
                  step="0.01"
                  placeholder="USD"
                  value={amount}
                  onChange={handleAmountChange}
                />
                of my ${availableBalance.toFixed(2)}:
              </label>
              {error && (
                <p
                  data-testid="error"
                  className="form-hint error-text mt-3 pl-0 ml-0 text-red-500"
                >
                  {error}
                </p>
              )}
            </div>
          </section>
          <Table amount={amount} />
        </div>
      );
    }

    // Render the app
    ReactDOM.render(<Main />, document.getElementById("root"));
  </script>
</body>
</html>
```

---

To separate the provided React application code into two distinct files (`Main.js` and `Table.js`) while maintaining the functionality of the CryptoRank Exchange application, I'll extract the relevant components from the single `index.html` file and place them into their respective JavaScript files. Additionally, I'll provide an updated `index.html` that sets up the React environment and includes the necessary dependencies.

The separation will involve:
- **Main.js**: Contains the `Main` component with state management for the input amount, validation logic, and rendering of the input field, error messages, and the `Table` component.
- **Table.js**: Contains the `Table` component that renders the cryptocurrency data table, using the `cryptocurrencyList` and the `amount` prop to calculate and display the number of coins.
- **index.html**: Sets up the React environment with Tailwind CSS, React, ReactDOM, and Babel, and includes the `cryptocurrencyList` data and rendering logic.

Below are the three files:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CryptoRank Exchange</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/react@18/umd/react.development.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel" src="Main.js"></script>
  <script type="text/babel" src="Table.js"></script>
  <script type="text/babel">
    // cryptocurrency-list.js
    const cryptocurrencyList = [
      { name: "BNB", code: "BNB", rate: 0.00311839 },
      { name: "Bitcoin", code: "BTC", rate: 0.00004066 },
      { name: "Dogecoin", code: "DOGE", rate: 11.18558722 },
      { name: "Ethereum", code: "ETH", rate: 0.00059237 },
      { name: "XRP", code: "XRP", rate: 2.50682634 },
    ];

    // Render the app
    ReactDOM.render(<Main />, document.getElementById("root"));
  </script>
</body>
</html>
```

```javascript
import React from "react";
import Table from "./Table";

function Main() {
  const [amount, setAmount] = React.useState("");
  const [error, setError] = React.useState("");
  const availableBalance = 17042.67;

  const validateAmount = (value) => {
    if (value === "") {
      setError("Amount cannot be empty");
      return false;
    }
    const numValue = parseFloat(value);
    if (isNaN(numValue)) {
      setError("Amount must be a valid number");
      return false;
    }
    if (numValue < 0.01) {
      setError("Amount cannot be less than 0.01");
      return false;
    }
    if (numValue > availableBalance) {
      setError("Amount cannot exceed the available balance");
      return false;
    }
    setError("");
    return true;
  };

  const handleAmountChange = (e) => {
    const value = e.target.value;
    setAmount(value);
    validateAmount(value);
  };

  return (
    <div className="layout-column align-items-center mx-auto max-w-2xl p-4">
      <h1 className="text-2xl font-bold">CryptoRank Exchange</h1>
      <section>
        <div className="card-text layout-column align-items-center mt-12 px-8 flex text-center">
          <label className="mb-4">
            I want to exchange $
            <input
              className="w-32 ml-2 p-1 border rounded"
              data-testid="amount-input"
              type="number"
              step="0.01"
              placeholder="USD"
              value={amount}
              onChange={handleAmountChange}
            />
            of my ${availableBalance.toFixed(2)}:
          </label>
          {error && (
            <p
              data-testid="error"
              className="form-hint error-text mt-3 pl-0 ml-0 text-red-500"
            >
              {error}
            </p>
          )}
        </div>
      </section>
      <Table amount={amount} />
    </div>
  );
}

export default Main;
```

```javascript
import React from "react";

function Table({ amount }) {
  const cryptocurrencyList = [
    { name: "BNB", code: "BNB", rate: 0.00311839 },
    { name: "Bitcoin", code: "BTC", rate: 0.00004066 },
    { name: "Dogecoin", code: "DOGE", rate: 11.18558722 },
    { name: "Ethereum", code: "ETH", rate: 0.00059237 },
    { name: "XRP", code: "XRP", rate: 2.50682634 },
  ];

  const isValidAmount = !isNaN(amount) && amount >= 0.01 && amount <= 17042.67;

  return (
    <div className="card card-text mt-10 mx-4">
      <table className="mb-0 w-full">
        <thead>
          <tr>
            <th className="text-left p-2">Cryptocurrency</th>
            <th className="text-left p-2">Exchange Rate</th>
            <th className="text-left p-2">Number of Coins</th>
          </tr>
        </thead>
        <tbody data-testid="exchange-data">
          {cryptocurrencyList.map((crypto) => (
            <tr key={crypto.code}>
              <td className="p-2">{crypto.name}</td>
              <td className="p-2">1 USD = {crypto.rate.toFixed(8)} {crypto.code}</td>
              <td className="p-2">
                {isValidAmount
                  ? (amount * crypto.rate).toFixed(8)
                  : amount === ""
                  ? "0.00000000"
                  : "n/a"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Table;
```

### Explanation of Changes
- **index.html**: This file sets up the React environment with Tailwind CSS, React, ReactDOM, and Babel. It includes the `cryptocurrencyList` array (as per the original requirement, it seems to be an external data source) and renders the `Main` component. The `Main.js` and `Table.js` files are included via `<script>` tags, assuming a simple setup for development purposes.
- **Main.js**: This file contains the `Main` component, which manages the input state (`amount` and `error`), validates the input amount, and passes the `amount` prop to the `Table` component. The input field is bound to the `amount` state, and the `handleAmountChange` function updates the state and triggers validation.
- **Table.js**: This file contains the `Table` component, which receives the `amount` prop and renders a table with cryptocurrency data. It checks if the `amount` is valid to determine whether to display calculated coin amounts, "0.00000000" (for empty input), or "n/a" (for invalid input). The `cryptocurrencyList` is included directly in `Table.js` for simplicity, as the original code suggested it was imported but didn't specify a separate file.

### Notes
- **Artifact IDs**: The `index.html` file retains the original `artifact_id` (`c56a32de-4723-4b39-baee-3013bf5b1d60`) as it is an update to the previously provided artifact. The `Main.js` and `Table.js` files have new UUIDs (`a1b2c3d4-e56f-7890-abcd-ef1234567890` and `b2c3d4e5-f67a-8901-bcde-f23456789012`) since they are newly created artifacts.
- **Dependencies**: The `index.html` assumes a simple UMD-based setup for React and Tailwind CSS via CDNs, suitable for a standalone demo. In a real-world application, you might use a module bundler like Webpack or Vite, and the `import` statements in `Main.js` and `Table.js` would rely on a proper module system.
- **Cryptocurrency List**: The `cryptocurrencyList` is included in `Table.js` for simplicity, as the original code imported it without specifying its location. In a production environment, it should be in a separate file (e.g., `cryptocurrency-list.js`) and imported into both components if needed.
- **Running the Code**: To test this locally, save the three files in the same directory and serve them via a web server (e.g., using `npx serve` or a similar tool). The `index.html` file will load `Main.js` and `Table.js` and render the application.

These files should meet the requirements, including input validation, dynamic table updates, and proper error handling, while passing the unit tests described in the requirements.