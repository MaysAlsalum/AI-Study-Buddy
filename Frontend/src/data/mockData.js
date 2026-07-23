// Mock responses matching the backend JSON contract exactly.
// When the real FastAPI backend is connected, replace the
// _process() call in Dashboard.jsx with an HTTP fetch — zero UI changes.

const _SUMMARY =
  'Machine learning is a subfield of artificial intelligence concerned with building ' +
  'systems that learn from data to make predictions or decisions without being explicitly ' +
  'programmed. The field is broadly divided into supervised learning, where models are ' +
  'trained on labeled examples; unsupervised learning, where patterns are discovered ' +
  'from unlabeled data; and reinforcement learning, where an agent learns by interacting ' +
  'with an environment. Central to all approaches is the concept of a model — a ' +
  'mathematical function fitted to training data — and a loss function that quantifies ' +
  'prediction error. Optimization algorithms such as gradient descent iteratively adjust ' +
  'model parameters to minimize this loss. Neural networks, organized as layers of ' +
  'interconnected nodes, form the basis of deep learning and have achieved state-of-the-art ' +
  'performance across vision, language, and structured data tasks.'

const _KEY_TOPICS = [
  'Supervised Learning',
  'Unsupervised Learning',
  'Reinforcement Learning',
  'Neural Networks',
  'Gradient Descent',
  'Loss Functions',
  'Overfitting and Regularization',
]

const _DEFINITIONS = [
  {
    term: 'Supervised Learning',
    definition:
      'A machine learning paradigm in which a model is trained on a labeled dataset, ' +
      'where each input is paired with the correct output. The model learns to map ' +
      'inputs to outputs and is evaluated on unseen examples.',
  },
  {
    term: 'Gradient Descent',
    definition:
      'An iterative optimization algorithm that updates model parameters in the direction ' +
      'opposite to the gradient of the loss function, thereby minimizing prediction error ' +
      'over successive training steps.',
  },
  {
    term: 'Overfitting',
    definition:
      'A modeling error that occurs when a model learns the training data too precisely, ' +
      'including its noise and random fluctuations, resulting in poor generalization ' +
      'to new, unseen data.',
  },
  {
    term: 'Neural Network',
    definition:
      'A computational model composed of layers of interconnected nodes (neurons) that ' +
      'transform inputs through learned weight matrices and non-linear activation functions ' +
      'to produce output predictions.',
  },
  {
    term: 'Loss Function',
    definition:
      'A mathematical function that measures the discrepancy between a model\'s predictions ' +
      'and the true target values. Minimizing the loss function is the primary objective ' +
      'during model training.',
  },
]

const _SECURITY = { is_safe: true, risk_level: 'Low', warnings: [] }

export const MOCK_QUIZ_STATE = {
  file_name: 'introduction_to_machine_learning.pdf',
  study_days: 5,
  goal: 'quiz',
  raw_text: '',
  summary: _SUMMARY,
  key_topics: _KEY_TOPICS,
  definitions: _DEFINITIONS,
  quiz: [
    {
      question: 'Which of the following best describes supervised learning?',
      type: 'mcq',
      choices: [
        'Training a model on labeled input-output pairs',
        'Discovering patterns in unlabeled data',
        'Learning through trial-and-error with environmental rewards',
        'Reducing the dimensionality of a dataset',
      ],
      correct_answer: 'Training a model on labeled input-output pairs',
      explanation:
        'Supervised learning requires a labeled dataset where each training example ' +
        'has a corresponding ground-truth output. The model learns a mapping function ' +
        'and is evaluated by comparing its predictions against known labels.',
    },
    {
      question: 'What is the primary purpose of a loss function in machine learning?',
      type: 'mcq',
      choices: [
        'To generate new training data',
        'To measure the error between predictions and true values',
        'To initialize the weights of a neural network',
        'To select the learning rate for optimization',
      ],
      correct_answer: 'To measure the error between predictions and true values',
      explanation:
        'A loss function quantifies how far a model\'s predictions deviate from ' +
        'the actual target values. Minimizing this function during training drives ' +
        'the model toward better predictive accuracy.',
    },
    {
      question: 'Which problem does regularization primarily address?',
      type: 'mcq',
      choices: [
        'Underfitting on the training set',
        'Slow convergence of gradient descent',
        'Overfitting to the training data',
        'Imbalanced class distribution',
      ],
      correct_answer: 'Overfitting to the training data',
      explanation:
        'Regularization techniques such as L1 (Lasso), L2 (Ridge), and dropout ' +
        'add a penalty to the loss function or randomly deactivate neurons, ' +
        'discouraging the model from fitting noise in the training data and ' +
        'improving generalization.',
    },
    {
      question: 'In gradient descent, in which direction are model parameters updated?',
      type: 'mcq',
      choices: [
        'In the direction of the gradient of the loss function',
        'Opposite to the gradient of the loss function',
        'Perpendicular to the gradient of the loss function',
        'Randomly, independent of the gradient',
      ],
      correct_answer: 'Opposite to the gradient of the loss function',
      explanation:
        'Gradient descent moves parameters in the direction that most steeply ' +
        'decreases the loss — the negative gradient direction. This iterative ' +
        'process continues until the loss converges to a minimum.',
    },
    {
      question: 'What distinguishes deep learning from classical machine learning?',
      type: 'mcq',
      choices: [
        'Deep learning requires labeled data; classical ML does not',
        'Deep learning uses multi-layered neural networks to learn hierarchical features',
        'Deep learning is limited to image classification tasks',
        'Deep learning does not use gradient-based optimization',
      ],
      correct_answer:
        'Deep learning uses multi-layered neural networks to learn hierarchical features',
      explanation:
        'Deep learning employs neural networks with many hidden layers, enabling ' +
        'the automatic extraction of increasingly abstract feature representations ' +
        'from raw data. This removes the need for manual feature engineering ' +
        'that classical ML methods typically require.',
    },
  ],
  study_plan: [],
  security: _SECURITY,
}

export const MOCK_STUDY_PLAN_STATE = {
  file_name: 'introduction_to_machine_learning.pdf',
  study_days: 5,
  goal: 'study_plan',
  raw_text: '',
  summary: _SUMMARY,
  key_topics: _KEY_TOPICS,
  definitions: _DEFINITIONS,
  quiz: [],
  study_plan: [
    { day: 1, topics: ['Supervised Learning', 'Loss Functions'] },
    { day: 2, topics: ['Gradient Descent', 'Review: Supervised Learning'] },
    { day: 3, topics: ['Unsupervised Learning', 'Reinforcement Learning', 'Review: Loss Functions'] },
    { day: 4, topics: ['Neural Networks', 'Review: Gradient Descent', 'Review: Unsupervised Learning'] },
    { day: 5, topics: ['Overfitting and Regularization', 'Review: Neural Networks', 'Review: Reinforcement Learning'] },
  ],
  security: _SECURITY,
}

export function buildState(file_name, study_days, goal) {
  const base = goal === 'quiz' ? MOCK_QUIZ_STATE : MOCK_STUDY_PLAN_STATE
  return { ...base, file_name, study_days, goal }
}
