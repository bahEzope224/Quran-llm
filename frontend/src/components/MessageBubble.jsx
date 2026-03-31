import AnswerCard from './AnswerCard.jsx';

export default function MessageBubble({ message }) {
  const isAssistant = message.role === 'assistant';

  return (
    <article
      className={`message-row ${isAssistant ? 'assistant' : 'user'}`}
      aria-label={isAssistant ? 'Message assistant' : 'Message utilisateur'}
    >
      {isAssistant ? (
        <AnswerCard title={message.title} content={message.content} />
      ) : (
        <div className="message-bubble">{message.content}</div>
      )}
    </article>
  );
}
