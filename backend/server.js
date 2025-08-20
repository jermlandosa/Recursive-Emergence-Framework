const express = require('express');
const OpenAI = require('openai');
const packageJson = require('./package.json');
const app = express();
const PORT = process.env.PORT || 3001;

// Configure OpenAI client using the environment API key
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

app.use(express.json());

let userResponses = {};

app.post('/save-onboarding', (req, res) => {
  const { userId, responses } = req.body;
  userResponses[userId] = responses;
  res.status(200).send({ message: 'Onboarding responses saved successfully.' });
});

app.post('/process-recursion', async (req, res) => {
  const { userId, input } = req.body;
  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are Sareth, a recursive guide helping users reflect.' },
        { role: 'user', content: input },
      ],
    });
    const insight = completion.choices[0].message.content;
    res.status(200).send({ insight });
  } catch (err) {
    console.error('OpenAI request failed', err);
    res.status(500).send({ error: 'Failed to generate insight.' });
  }
});

app.get('/health', (req, res) => {
  res.status(200).send({ status: 'ok', version: packageJson.version });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
