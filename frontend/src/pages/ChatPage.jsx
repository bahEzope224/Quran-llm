import {
  Show,
  SignInButton,
  SignOutButton,
  SignUpButton,
  useUser,
} from '@clerk/react';
import { Link } from 'react-router-dom';
import { useEffect, useMemo, useRef, useState } from 'react';

const rawApiUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
// Securite : Si l'URL ne commence pas par http, on force le protocole pour eviter les erreurs de chemin relatif
const API_BASE_URL = rawApiUrl.startsWith('http') ? rawApiUrl : `https://${rawApiUrl}`;
const CHAT_STORAGE_KEY = 'ilm-ai-chat-history-v1';

const legalSchools = ['Hanafi', 'Maliki', 'Shafi‘i', 'Hanbali'];
const languages = ['Francais', 'Arabe', 'Anglais'];
const modes = ['Clair', 'Approfondi', 'Concise'];

// Les fallbacks de developpement ont ete supprimes pour la mise en production.

const fallbackProfile = {
  name: 'Ibrahima Bah',
  avatar_initials: 'IB',
  legal_school: 'Maliki',
  language: 'Francais',
  mode: 'Clair',
  notifications_enabled: true,
};

function truncateTitle(text) {
  const normalized = text.replace(/\s+/g, ' ').trim();
  if (!normalized) {
    return 'Nouvelle discussion';
  }
  return normalized.length > 56 ? `${normalized.slice(0, 56).trim()}...` : normalized;
}

function createEmptyConversation() {
  const timestamp = new Date().toISOString();
  return {
    id: `conversation-${crypto.randomUUID()}`,
    title: 'Nouvelle discussion',
    createdAt: timestamp,
    updatedAt: timestamp,
    messages: [],
  };
}

function loadStoredChatState() {
  if (typeof window === 'undefined') {
    const initialConversation = createEmptyConversation();
    return {
      conversations: [initialConversation],
      activeConversationId: initialConversation.id,
    };
  }

  try {
    const rawValue = window.localStorage.getItem(CHAT_STORAGE_KEY);
    if (!rawValue) {
      throw new Error('empty_storage');
    }

    const parsedValue = JSON.parse(rawValue);
    if (!Array.isArray(parsedValue.conversations) || !parsedValue.conversations.length) {
      throw new Error('invalid_conversations');
    }

    const activeConversationExists = parsedValue.conversations.some(
      (conversation) => conversation.id === parsedValue.activeConversationId
    );

    return {
      conversations: parsedValue.conversations,
      activeConversationId: activeConversationExists
        ? parsedValue.activeConversationId
        : parsedValue.conversations[0].id,
    };
  } catch {
    const initialConversation = createEmptyConversation();
    return {
      conversations: [initialConversation],
      activeConversationId: initialConversation.id,
    };
  }
}

function toSourceCard(source, index) {
  const fallbackSourceName =
    source.type === 'quran'
      ? 'Quran'
      : source.type === 'tafsir'
        ? 'Tafsir'
        : 'Hadith';
  const displaySourceName =
    source.type === 'quran' ? 'Quran' : (source.source ?? fallbackSourceName);

  return {
    id: `${source.type}-${index}`,
    icon:
      source.type === 'quran'
        ? 'auto_stories'
        : source.type === 'tafsir'
          ? 'menu_book'
          : 'history_edu',
    source: displaySourceName,
    reference: source.ref,
    role: source.role,
    type: source.type,
    title: source.arabic ?? '',
    translation: source.text,
    content: source.text,
  };
}

function buildEvidenceHighlights(sources) {
  return sources.map((source, index) => ({
    id: `${source.type}-${index}-highlight`,
    title:
      source.type === 'quran'
        ? 'Ancrage coranique'
        : source.type === 'tafsir'
          ? 'Lecture savante'
          : 'Appui prophetique',
    value: source.ref,
    detail: source.role,
  }));
}

function SourceCard({ card }) {
  if (card.type === 'quran') {
    return (
      <article className={`source-card ${card.type}`}>
        <div className="source-card-header">
          <span className="material-symbols-outlined">{card.icon}</span>
          <div className="source-card-meta">
            <span className="source-card-source">{card.source}</span>
            <span className="source-card-reference">{card.reference}</span>
          </div>
        </div>
        <p className="arabic-text" dir="rtl">
          {card.title}
        </p>
        <p className="source-card-text source-card-translation">"{card.translation}"</p>
      </article>
    );
  }

  return (
    <article className={`source-card ${card.type}`}>
      <div className="source-card-header">
        <span className="material-symbols-outlined">{card.icon}</span>
        <div className="source-card-meta">
          <span className="source-card-source">{card.source}</span>
          <span className="source-card-reference">{card.reference}</span>
        </div>
      </div>
      <p className={`source-card-text ${card.type === 'hadith' ? 'italic' : ''}`}>
        "{card.content}"
      </p>
    </article>
  );
}

function createAssistantMessage(response) {
  return {
    id: `assistant-${crypto.randomUUID()}`,
    role: 'assistant',
    answer: response.answer,
    displayedAnswer: '',
    sources: response.sources,
    isComplete: false,
    feedback: null,
  };
}

export default function ChatPage() {
  const { isLoaded: isUserLoaded, user } = useUser();
  const [activeView, setActiveView] = useState('response');
  const [activeScreen, setActiveScreen] = useState('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [questionInput, setQuestionInput] = useState('');
  const [profile, setProfile] = useState(fallbackProfile);
  const [feedbackStore, setFeedbackStore] = useState({});

  // Ouverture intelligente de la sidebar au montage (Desktop uniquement)
  useEffect(() => {
    if (window.innerWidth > 1024) {
      setIsSidebarOpen(true);
    }
  }, []);

  const handleFeedback = async (message, type, comment = null) => {
    // Si c'est un Down initial sans commentaire, on montre juste la zone de texte
    if (type === 'down' && comment === null) {
      setFeedbackStore(prev => ({
        ...prev,
        [message.id]: { type: 'down', comment: '', submitted: false, showCommentBox: true }
      }));
      return;
    }

    // Sinon, on cherche la question utilisateur dans l'historique des messages
    const currentMessageIndex = messages.findIndex((m) => m.id === message.id);
    const userMessage = messages
      .slice(0, Math.max(0, currentMessageIndex))
      .reverse()
      .find((m) => m.role === 'user');

    const question = userMessage ? userMessage.content : "Question inconnue";

    // Envoi au backend
    try {
      const response = await fetch(`${API_BASE_URL}/chat/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          answer: message.answer || message.displayedAnswer,
          feedback: type,
          comment: comment,
          sources: message.sources || [],
          profile: profile
        })
      });

      if (response.ok) {
        setFeedbackStore(prev => ({
          ...prev,
          [message.id]: { type, comment, submitted: true, showCommentBox: false }
        }));
      }
    } catch (error) {
      console.error("Erreur lors de l'envoi du feedback:", error);
    }
  };

  const [chatState, setChatState] = useState(() => loadStoredChatState());
  const [isLoadingChat, setIsLoadingChat] = useState(false);
  const [isAnimatingAnswer, setIsAnimatingAnswer] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [chatError, setChatError] = useState('');
  const [profileError, setProfileError] = useState('');
  const abortControllerRef = useRef(null);
  const animationTimerRef = useRef(null);
  const activeAssistantIdRef = useRef(null);
  const chatEndRef = useRef(null);
  const activeConversationIdRef = useRef(chatState.activeConversationId);

  const isGenerating = isLoadingChat || isAnimatingAnswer;
  const conversations = chatState.conversations;
  const activeConversation =
    conversations.find((conversation) => conversation.id === chatState.activeConversationId) ??
    conversations[0];
  const messages = activeConversation?.messages ?? [];

  useEffect(() => {
    activeConversationIdRef.current = chatState.activeConversationId;
  }, [chatState.activeConversationId]);

  useEffect(() => {
    window.localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chatState));
  }, [chatState]);

  useEffect(() => {
    async function loadProfile() {
      setIsLoadingProfile(true);
      setProfileError('');

      try {
        const response = await fetch(`${API_BASE_URL}/user/profile`);
        if (!response.ok) {
          throw new Error('profile_request_failed');
        }

        const data = await response.json();
        setProfile(data);
      } catch {
        setProfileError('Profil indisponible pour le moment.');
      } finally {
        setIsLoadingProfile(false);
      }
    }

    loadProfile();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, activeView, chatState.activeConversationId]);

  useEffect(() => () => {
    abortControllerRef.current?.abort();
    if (animationTimerRef.current) {
      window.clearInterval(animationTimerRef.current);
    }
  }, []);

  function updateConversation(conversationId, updater) {
    setChatState((currentState) => ({
      ...currentState,
      conversations: currentState.conversations.map((conversation) => {
        if (conversation.id !== conversationId) {
          return conversation;
        }

        const updatedConversation = updater(conversation);
        return {
          ...updatedConversation,
          updatedAt: new Date().toISOString(),
        };
      }),
    }));
  }

  function updateActiveConversation(updater) {
    const currentConversationId = activeConversationIdRef.current;
    if (!currentConversationId) {
      return;
    }
    updateConversation(currentConversationId, updater);
  }

  function finalizeAssistantMessage(messageId, finalAnswer, finalSources) {
    updateActiveConversation((conversation) => ({
      ...conversation,
      messages: conversation.messages.map((message) =>
        message.id === messageId
          ? {
              ...message,
              answer: finalAnswer,
              displayedAnswer: finalAnswer,
              sources: finalSources,
              isComplete: true,
            }
          : message
      ),
    }));
  }

  function animateAssistantAnswer(messageId, finalAnswer, finalSources) {
    if (animationTimerRef.current) {
      window.clearInterval(animationTimerRef.current);
    }

    const answerCharacters = Array.from(finalAnswer);
    const totalLength = answerCharacters.length;
    const step = totalLength > 700 ? 18 : totalLength > 320 ? 10 : 5;
    let cursor = 0;

    setIsAnimatingAnswer(true);
    activeAssistantIdRef.current = messageId;

    animationTimerRef.current = window.setInterval(() => {
      cursor = Math.min(cursor + step, totalLength);
      const partialAnswer = answerCharacters.slice(0, cursor).join('');

      updateActiveConversation((conversation) => ({
        ...conversation,
        messages: conversation.messages.map((message) =>
          message.id === messageId
            ? {
                ...message,
                displayedAnswer: partialAnswer,
              }
            : message
        ),
      }));

      if (cursor >= totalLength) {
        window.clearInterval(animationTimerRef.current);
        animationTimerRef.current = null;
        finalizeAssistantMessage(messageId, finalAnswer, finalSources);
        setIsAnimatingAnswer(false);
        activeAssistantIdRef.current = null;
      }
    }, 20);
  }

  function stopGeneration() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (animationTimerRef.current) {
      window.clearInterval(animationTimerRef.current);
      animationTimerRef.current = null;
    }

    const activeAssistantId = activeAssistantIdRef.current;
    if (activeAssistantId) {
      updateActiveConversation((conversation) => ({
        ...conversation,
        messages: conversation.messages.map((message) =>
          message.id === activeAssistantId
            ? {
                ...message,
                isComplete: true,
                displayedAnswer:
                  message.displayedAnswer || 'Reponse interrompue. Posez une nouvelle question.',
              }
            : message
        ),
      }));
    }

    activeAssistantIdRef.current = null;
    setIsLoadingChat(false);
    setIsAnimatingAnswer(false);
  }

  function createNewConversation() {
    stopGeneration();
    const nextConversation = createEmptyConversation();
    setChatError('');
    setActiveView('response');
    setIsSidebarOpen(false);
    setChatState((currentState) => ({
      conversations: [nextConversation, ...currentState.conversations],
      activeConversationId: nextConversation.id,
    }));
  }

  function selectConversation(conversationId) {
    if (conversationId === chatState.activeConversationId) {
      return;
    }

    stopGeneration();
    setChatError('');
    setActiveView('response');
    setIsSidebarOpen(false);
    setChatState((currentState) => ({
      ...currentState,
      activeConversationId: conversationId,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedQuestion = questionInput.trim();
    if (!trimmedQuestion || !activeConversation) {
      return;
    }

    const userMessage = {
      id: `user-${crypto.randomUUID()}`,
      role: 'user',
      content: trimmedQuestion,
    };
    const assistantMessage = createAssistantMessage({
      answer: '',
      sources: [],
    });

    const nextTitle =
      activeConversation.messages.length === 0
        ? truncateTitle(trimmedQuestion)
        : activeConversation.title;

    setQuestionInput('');
    updateActiveConversation((conversation) => ({
      ...conversation,
      title: nextTitle,
      messages: [...conversation.messages, userMessage, assistantMessage],
    }));
    setIsSidebarOpen(false);
    setIsLoadingChat(true);
    setChatError('');
    activeAssistantIdRef.current = assistantMessage.id;
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          question: trimmedQuestion,
          mode: activeView,
          profile: {
            legal_school: profile.legal_school,
            language: profile.language,
            mode: profile.mode,
            notifications_enabled: profile.notifications_enabled,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('chat_request_failed');
      }

      const data = await response.json();
      setActiveView('response');
      setIsLoadingChat(false);
      abortControllerRef.current = null;
      animateAssistantAnswer(assistantMessage.id, data.answer, data.sources);
    } catch {
      const wasAborted = abortControllerRef.current?.signal.aborted;
      abortControllerRef.current = null;
      setIsLoadingChat(false);
      if (wasAborted) {
        return;
      }

      setChatError('Le serveur ILM AI est temporairement indisponible. Veuillez verifier votre connexion ou reessayer plus tard.');
      finalizeAssistantMessage(
        assistantMessage.id, 
        "Désolé, je ne peux pas répondre pour le moment car le serveur de recherche est hors ligne. Veuillez réessayer dans quelques instants.", 
        []
      );
    }
  }

  const sortedConversations = useMemo(
    () =>
      [...conversations].sort(
        (left, right) => new Date(right.updatedAt).getTime() - new Date(left.updatedAt).getTime()
      ),
    [conversations]
  );

  const clerkInitials = [user?.firstName?.[0], user?.lastName?.[0]]
    .filter(Boolean)
    .join('')
    .toUpperCase();
  const clerkFullName =
    [user?.firstName, user?.lastName].filter(Boolean).join(' ') ||
    user?.username ||
    user?.primaryEmailAddress?.emailAddress ||
    null;
  const displayName = clerkFullName || profile.name;
  const displayInitials = clerkInitials || profile.avatar_initials;
  const displayAvatarUrl = user?.imageUrl ?? null;

  return (
    <div className="ilm-chat-page">
      <header className="top-app-bar">
        <div className="top-bar-left">
          <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <img src="/logo.svg" alt="ʿIlm Logo" className="brand-logo" />
            <span className="brand-title">ILM AI</span>
          </Link>
        </div>

        <div className="top-bar-center">
          {activeScreen !== 'chat' && (
            <span className="profile-header-label">Mon profil</span>
          )}
        </div>

        <div className="top-bar-right">
          <div className="top-bar-actions">
            {activeScreen === 'chat' && (
              <div className="view-toggle" aria-label="Changer de mode de reponse">
                <button
                  className={`toggle-pill ${activeView === 'response' ? 'active' : ''}`}
                  type="button"
                  onClick={() => setActiveView('response')}
                >
                  Reponse
                </button>
                <button
                  className={`toggle-pill ${activeView === 'proofs' ? 'active' : ''}`}
                  type="button"
                  onClick={() => setActiveView('proofs')}
                >
                  Preuves
                </button>
              </div>
            )}
            
            <button
              className={`icon-button profile-button ${activeScreen === 'profile' ? 'active' : ''}`}
              type="button"
              aria-label={activeScreen === 'profile' ? 'Revenir au chat' : 'Acceder au profil'}
              onClick={() =>
                setActiveScreen((currentScreen) =>
                  currentScreen === 'profile' ? 'chat' : 'profile'
                )
              }
            >
              <span className="material-symbols-outlined">
                {activeScreen === 'profile' ? 'chat_bubble' : 'person'}
              </span>
            </button>

            <div className="session-actions">
              <Show when="signed-out">
                <SignInButton mode="modal">
                  <button className="auth-ghost-button header-auth-button" type="button">
                    Connexion
                  </button>
                </SignInButton>
              </Show>
            </div>
          </div>
        </div>
      </header>

      {/* Overlay pour fermer la sidebar sur mobile en cliquant a l'exterieur */}
      {isSidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)}></div>
      )}

      <main className="chat-main-container">
        {activeScreen === 'chat' ? (
          <div className={`chat-layout ${!isSidebarOpen ? 'sidebar-closed' : ''}`}>
            {/* Rail d'icones lateral */}
            <nav className="chat-sidebar-rail" aria-label="Rail de navigation">
              <button
                className="sidebar-rail-button"
                type="button"
                onClick={() => setIsSidebarOpen((currentValue) => !currentValue)}
                aria-label={isSidebarOpen ? 'Masquer historique' : 'Afficher historique'}
              >
                <span className="material-symbols-outlined">
                  {isSidebarOpen ? 'left_panel_close' : 'left_panel_open'}
                </span>
              </button>

              <button
                className="sidebar-rail-button"
                type="button"
                onClick={createNewConversation}
                aria-label="Nouvelle discussion"
              >
                <span className="material-symbols-outlined">edit</span>
              </button>
            </nav>

            {/* Carte Historique (Style Photo 2) */}
            <nav className={`chat-sidebar ${!isSidebarOpen ? 'closed' : ''}`} aria-label="Historique des discussions">
              <div className="chat-sidebar-header">
                <p className="sidebar-kicker">DISCUSSIONS</p>
                <h2>Historique</h2>
                <button 
                  className="new-chat-btn-sidebar"
                  onClick={createNewConversation}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>add</span>
                  NOUVELLE
                </button>
              </div>

              <div className="conversation-list">
                {sortedConversations.map((conversation) => {
                  const previewMessage = conversation.messages.find((message) => message.role === 'user');

                  return (
                    <button
                      key={conversation.id}
                      className={`conversation-item ${
                        conversation.id === chatState.activeConversationId ? 'active' : ''
                      }`}
                      type="button"
                      onClick={() => selectConversation(conversation.id)}
                    >
                      <strong>{conversation.title}</strong>
                      <p>{previewMessage?.content ?? 'Aucun message pour le moment.'}</p>
                    </button>
                  );
                })}
              </div>
            </nav>

            <section className={`chat-panel ${isSidebarOpen ? '' : 'expanded'}`}>
              <section className="chat-thread" aria-label="Historique de conversation">
                {chatError ? <p className="status-banner warning">{chatError}</p> : null}

                {!messages.length ? (
                  <article className="empty-chat-state">
                    <span className="material-symbols-outlined">forum</span>
                    <h2>Nouvelle discussion</h2>
                    <p>Posez votre premiere question. Cette discussion restera disponible apres rafraichissement.</p>
                  </article>
                ) : null}

                {messages.map((message) => {
                  if (message.role === 'user') {
                    return (
                      <div key={message.id} className="user-message-row message-enter">
                        <article className="user-message">
                          <p>{message.content}</p>
                        </article>
                      </div>
                    );
                  }

                  const sourceCards = message.sources.map(toSourceCard);
                  const evidenceHighlights = buildEvidenceHighlights(message.sources);

                  return (
                    <div key={message.id} className="assistant-stack message-enter">
                      {activeView === 'response' ? (
                        <>
                          <article className="assistant-response-card">
                            <div className="assistant-card-header">
                              <div className="reliable-badge">
                                <span className="material-symbols-outlined fill">verified</span>
                                <span>Fiable</span>
                              </div>

                              <button
                                className="copy-button"
                                type="button"
                                onClick={() =>
                                  navigator.clipboard.writeText(message.displayedAnswer || message.answer)
                                }
                              >
                                <span className="material-symbols-outlined">content_copy</span>
                                <span>Copier</span>
                              </button>
                            </div>

                            <p
                              className={`assistant-response-text ${
                                message.isComplete ? '' : 'is-streaming'
                              }`}
                            >
                              {message.displayedAnswer}
                            </p>

                            {message.isComplete && message.sources.length ? (
                              <div className="tag-list" aria-label="Etiquettes">
                                {message.sources.map((source) => (
                                  <span
                                    key={`${message.id}-${source.type}-${source.ref}`}
                                    className="topic-tag"
                                  >
                                    {source.type}
                                  </span>
                                ))}
                              </div>
                            ) : null}
                          </article>

                          {message.isComplete && sourceCards.length ? (
                            <div className="source-stack">
                              {sourceCards.map((card) => (
                                <SourceCard key={card.id} card={card} />
                              ))}
                            </div>
                          ) : null}

                          {/* Section Feedback - Deplacee a la fin pour eviter les doublons */}
                          {message.isComplete && (
                            <div className="message-feedback-container">
                              {!feedbackStore[message.id]?.submitted ? (
                                <>
                                  {!feedbackStore[message.id]?.showCommentBox ? (
                                    <div className="feedback-buttons">
                                      <button 
                                        className="feedback-btn up" 
                                        onClick={() => handleFeedback(message, 'up')}
                                        title="Utile"
                                      >
                                        <span className="material-symbols-outlined">thumb_up</span>
                                        <span>Utile</span>
                                      </button>
                                      <button 
                                        className="feedback-btn down" 
                                        onClick={() => handleFeedback(message, 'down')}
                                        title="Imprécis"
                                      >
                                        <span className="material-symbols-outlined">thumb_down</span>
                                        <span>Imprécis</span>
                                      </button>
                                    </div>
                                  ) : (
                                    <div className="feedback-comment-box">
                                      <p>Comment pourrions-nous être plus précis ?</p>
                                      <textarea 
                                        placeholder="Ex: la source du hadith manque de précision..."
                                        value={feedbackStore[message.id]?.comment || ''}
                                        onChange={(e) => setFeedbackStore(prev => ({
                                          ...prev,
                                          [message.id]: { ...prev[message.id], comment: e.target.value }
                                        }))}
                                      />
                                      <div className="comment-actions">
                                        <button 
                                          className="submit-comment-btn"
                                          onClick={() => handleFeedback(message, 'down', feedbackStore[message.id]?.comment)}
                                        >
                                          Envoyer le retour
                                        </button>
                                        <button 
                                          className="skip-comment-btn"
                                          onClick={() => handleFeedback(message, 'down', '')}
                                        >
                                          Passer
                                        </button>
                                      </div>
                                    </div>
                                  )}
                                </>
                              ) : (
                                <div className="feedback-success">
                                  <span className="material-symbols-outlined">check_circle</span>
                                  <span>{feedbackStore[message.id]?.type === 'up' ? 'Merci pour votre retour positif ! ✨' : 'Merci, votre retour nous aide à nous améliorer.'}</span>
                                </div>
                              )}
                            </div>
                          )}
                        </>
                      ) : (
                        <section className="proofs-panel" aria-label="Preuves et references">
                          <article className="proofs-overview-card">
                            <div className="proofs-overview-head">
                              <div>
                                <p className="proofs-kicker">Niveau de preuve</p>
                                <h2>Sources mobilisees pour justifier la reponse</h2>
                              </div>
                              <div className="proofs-score">
                                <span className="material-symbols-outlined fill">gpp_good</span>
                                <span>{message.sources.length} sources</span>
                              </div>
                            </div>

                            <p className="proofs-overview-text">
                              Cette reponse s&apos;appuie sur les references retournees par le backend
                              pour justifier le contenu principal et rendre les preuves consultables.
                            </p>

                            <div className="proofs-highlight-grid">
                              {evidenceHighlights.map((item) => (
                                <article key={item.id} className="proof-highlight-card">
                                  <span className="proof-highlight-title">{item.title}</span>
                                  <strong>{item.value}</strong>
                                  <p>{item.detail}</p>
                                </article>
                              ))}
                            </div>
                          </article>

                          <div className="proofs-evidence-list">
                            {sourceCards.map((card, index) => (
                              <article key={card.id} className={`proof-item ${card.type}`}>
                                <div className="proof-step">
                                  <span>{index + 1}</span>
                                </div>

                                <div className="proof-item-content">
                                  <div className="proof-item-header">
                                    <div className="proof-item-source">
                                      <span className="material-symbols-outlined">{card.icon}</span>
                                      <div>
                                        <p>{card.source}</p>
                                        <span>{card.reference}</span>
                                      </div>
                                    </div>

                                    <span className="proof-chip">
                                      {card.type === 'quran'
                                        ? 'Texte source'
                                        : card.type === 'tafsir'
                                          ? 'Explication'
                                          : 'Confirmation'}
                                    </span>
                                  </div>

                                  {card.type === 'quran' ? (
                                    <>
                                      <p className="arabic-text proof-arabic" dir="rtl">
                                        {card.title}
                                      </p>
                                      <p className="proof-excerpt">"{card.translation}"</p>
                                    </>
                                  ) : (
                                    <p
                                      className={`proof-excerpt ${
                                        card.type === 'hadith' ? 'italic' : ''
                                      }`}
                                    >
                                      "{card.content}"
                                    </p>
                                  )}
                                </div>
                              </article>
                            ))}
                          </div>
                        </section>
                      )}

                      {!message.isComplete && (
                        <div className="typing-indicator" aria-label="Assistant en train d'ecrire">
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                        </div>
                      )}
                    </div>
                  );
                })}

                <div ref={chatEndRef} />
              </section>
            </section>
          </div>
        ) : (
          <section className="profile-page" aria-label="Profil utilisateur">
            {profileError ? <p className="status-banner warning">{profileError}</p> : null}

            <article className="profile-hero">
              {displayAvatarUrl ? (
                <img className="profile-avatar-image" src={displayAvatarUrl} alt={displayName} />
              ) : (
                <div className="profile-avatar">{displayInitials}</div>
              )}
              <div className="profile-identity">
                <p className="profile-kicker">Compte</p>
                <h1>{displayName}</h1>
                {isUserLoaded && user?.primaryEmailAddress?.emailAddress ? (
                  <p className="profile-email">{user.primaryEmailAddress.emailAddress}</p>
                ) : null}
              </div>
            </article>

            <article className="profile-card">
              <div className="section-heading">
                <span className="material-symbols-outlined">tune</span>
                <h2>Preferences</h2>
              </div>

              <div className="settings-grid">
                <label className="setting-field">
                  <span>Ecole juridique</span>
                  <select value={profile.legal_school} onChange={() => {}} disabled={isLoadingProfile}>
                    {legalSchools.map((school) => (
                      <option key={school} value={school}>
                        {school}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="setting-field">
                  <span>Langue</span>
                  <select value={profile.language} onChange={() => {}} disabled={isLoadingProfile}>
                    {languages.map((language) => (
                      <option key={language} value={language}>
                        {language}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="setting-field">
                  <span>Mode</span>
                  <select value={profile.mode} onChange={() => {}} disabled={isLoadingProfile}>
                    {modes.map((mode) => (
                      <option key={mode} value={mode}>
                        {mode}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </article>

            <article className="profile-card">
              <div className="section-heading">
                <span className="material-symbols-outlined">auto_stories</span>
                <h2>Activite</h2>
              </div>

              <div className="activity-list">
                <button
                  className="activity-item"
                  type="button"
                  onClick={() => {
                    setActiveScreen('chat');
                    setIsSidebarOpen(true);
                  }}
                >
                  <div>
                    <strong>Historique</strong>
                    <p>Retrouver les dernières questions et réponses consultées.</p>
                  </div>
                  <span className="material-symbols-outlined">history</span>
                </button>

                <button
                  className="activity-item"
                  type="button"
                  onClick={() => {
                    createNewConversation();
                    setActiveScreen('chat');
                  }}
                >
                  <div>
                    <strong>Nouvelle discussion</strong>
                    <p>Poser une nouvelle question à l'IA dès maintenant.</p>
                  </div>
                  <span className="material-symbols-outlined">add_circle</span>
                </button>
              </div>
            </article>

            <article className="profile-card">
              <div className="section-heading">
                <span className="material-symbols-outlined">notifications</span>
                <h2>Notifications</h2>
              </div>

              <div className="notification-row">
                <div>
                  <strong>Rappels et nouveautes</strong>
                  <p>Recevoir les notifications importantes de l&apos;application.</p>
                </div>
                <label className="switch">
                  <input type="checkbox" checked={profile.notifications_enabled} readOnly />
                  <span className="switch-track">
                    <span className="switch-thumb" />
                  </span>
                </label>
              </div>
            </article>

            <article className="profile-card danger-card">
              <div className="section-heading">
                <span className="material-symbols-outlined">logout</span>
                <h2>Session</h2>
              </div>

              <div className="signout-row">
                <div>
                  <strong>Se deconnecter</strong>
                  <p>Fermer la session Clerk sur cet appareil.</p>
                </div>

                <Show when="signed-in">
                  <SignOutButton>
                    <button className="signout-button" type="button">
                      Se deconnecter
                    </button>
                  </SignOutButton>
                </Show>

                <Show when="signed-out">
                  <SignInButton mode="modal">
                    <button className="signout-button secondary" type="button">
                      Se connecter
                    </button>
                  </SignInButton>
                </Show>
              </div>
            </article>
          </section>
        )}
      </main>

      {activeScreen === 'chat' ? (
        <div className="composer-shell">
          <p className="composer-disclaimer">
            Avertissement : Ce service ne constitue pas une fatwa. Verifiez les reponses de l&apos;IA 
            aupres de sources authentiques. ILM AI decline toute responsabilite quant a l&apos;interpretation des resultats.
          </p>
          <form className="composer" onSubmit={handleSubmit}>
            <label className="sr-only" htmlFor="chat-question">
              Posez votre question
            </label>
            <input
              id="chat-question"
              type="text"
              placeholder="Posez votre question..."
              value={questionInput}
              onChange={(event) => setQuestionInput(event.target.value)}
            />

            <button
              className={`send-button ${isGenerating ? 'stop' : ''}`}
              type={isGenerating ? 'button' : 'submit'}
              aria-label={isGenerating ? 'Interrompre la reponse' : 'Envoyer'}
              onClick={isGenerating ? stopGeneration : undefined}
              disabled={!isGenerating && !questionInput.trim()}
            >
              <span className="material-symbols-outlined send-icon">
                {isGenerating ? 'stop' : 'arrow_upward'}
              </span>
            </button>
          </form>
        </div>
      ) : null}
    </div>
  );
}
