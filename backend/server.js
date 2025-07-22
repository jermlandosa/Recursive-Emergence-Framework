const express = require('express');
const packageJson = require('./package.json');
const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

let userResponses = {};

app.post('/save-onboarding', (req, res) => {
  const { userId, responses } = req.body;
  userResponses[userId] = responses;
  res.status(200).send({ message: 'Onboarding responses saved successfully.' });
});

app.post('/process-recursion', (req, res) => {
  const { userId, input } = req.body;
  const insight = `Processed insight for ${userId}: ${input}`;
  res.status(200).send({ insight });
});

app.get('/health', (req, res) => {
  res.status(200).send({ status: 'ok', version: packageJson.version });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
