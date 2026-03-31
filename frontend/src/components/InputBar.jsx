export default function InputBar() {
  return (
    <form className="input-bar">
      <label className="sr-only" htmlFor="chat-input">
        Envoyer un message
      </label>
      <input
        id="chat-input"
        type="text"
        placeholder="Pose une question sur un verset, un theme ou une sourate..."
      />
      <button type="submit">Envoyer</button>
    </form>
  );
}
