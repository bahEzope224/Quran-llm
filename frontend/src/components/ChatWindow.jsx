import MessageBubble from './MessageBubble.jsx';

export default function ChatWindow({ messages }) {
  return (
    <section className="chat-window" aria-label="Conversation">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </section>
  );
}
