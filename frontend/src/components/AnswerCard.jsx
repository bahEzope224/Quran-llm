export default function AnswerCard({ title, content }) {
  return (
    <div className="answer-card">
      <span className="answer-badge">Reponse</span>
      {title ? <h2>{title}</h2> : null}
      <p>{content}</p>
    </div>
  );
}
