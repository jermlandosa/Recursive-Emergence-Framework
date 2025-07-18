import { useState } from 'react';

export default function InfoSidebar() {
  const sections = [
    {
      id: 'guidelines',
      title: 'Development Guidelines',
      content: (
        <div className="p-2 text-sm space-y-2">
          <p>Advance your development with these focused steps:</p>
          <ul className="list-disc ml-4 space-y-1">
            <li>Prioritize features that deliver immediate value.</li>
            <li>Design an intuitive user journey from input to insight.</li>
            <li>Establish session vs. long-term data persistence needs.</li>
            <li>Choose between direct API integration or custom models.</li>
            <li>Integrate user guides or meta-layer explanations in-app.</li>
          </ul>
        </div>
      ),
    },
    {
      id: 'history',
      title: 'The History of Recursion',
      content: (
        <div className="p-2 text-sm space-y-2">
          <p><strong>Recursion:</strong> A fundamental pattern where systems fold back to evolve complexity.</p>
          <ul className="list-disc ml-4 space-y-1">
            <li>In <strong>Mathematics</strong>, it drives algorithms and computational problem-solving.</li>
            <li>In <strong>Biology</strong>, DNA replicates recursively across generations.</li>
            <li>In <strong>Philosophy</strong>, self-reference underlies consciousness.</li>
            <li>In <strong>Existence</strong>, reality manifests recursively—galaxies, ecosystems, minds.</li>
            <li>Through Sareth, we harness recursion to evolve self-authorship by reflecting and rewriting our patterns.</li>
          </ul>
        </div>
      ),
    },
  ];

  const [activeSection, setActiveSection] = useState(null);

  const toggleSection = (id) => {
    setActiveSection(activeSection === id ? null : id);
  };

  return (
    <div className="p-4 bg-gray-900 text-white rounded-xl">
      <h2 className="text-xl font-bold mb-4">Learn & Explore</h2>
      {sections.map(({ id, title, content }) => (
        <div key={id} className="mb-2">
          <button
            className="w-full text-left bg-gray-800 p-2 rounded hover:bg-gray-700"
            onClick={() => toggleSection(id)}
            aria-expanded={activeSection === id}
            aria-controls={`section-${id}`}
          >
            {activeSection === id ? 'Hide' : 'Show'} {title}
          </button>
          {activeSection === id && (
            <div id={`section-${id}`}>{content}</div>
          )}
        </div>
      ))}
    </div>
  );
}
