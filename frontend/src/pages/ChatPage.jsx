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
  }, [messages, chatState.activeConversationId]);

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

  function finalizeAssistantMessage(messageId, finalAnswer, finalSources, errorId = null) {
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
              error_id: errorId,
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
          mode: 'response',
          profile: {
            legal_school: profile.legal_school,
            language: profile.language,
            mode: profile.mode,
            notifications_enabled: profile.notifications_enabled,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const err = new Error('chat_request_failed');
        err.error_id = errorData.error_id;
        err.status = response.status;
        err.message = errorData.message || 'Le serveur est indisponible.';
        throw err;
      }

      const data = await response.json();
      setIsLoadingChat(false);
      abortControllerRef.current = null;
      animateAssistantAnswer(assistantMessage.id, data.answer, data.sources);
    } catch (err) {
      setChatError('');
      
      let finalMessage = err.message || "Désolé, je ne peux pas répondre pour le moment.";
      let finalErrorId = err.error_id;

      // Detection des erreurs reseau pures (Failed to fetch) ou serveur injoignable sans JSON
      if (err.message?.toLowerCase().includes('fetch') || !finalErrorId) {
        finalMessage = "Le serveur est momentanément injoignable (Perturbation réseau ou mise à jour de l'infrastructure). Veuillez réessayer dans quelques instants.";
        finalErrorId = "NET-001";
      }

      finalizeAssistantMessage(
        assistantMessage.id, 
        finalMessage, 
        [],
        finalErrorId
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
          <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <img src="/logo.svg" alt="ʿIlm Logo" className="brand-logo" />
            <div>
              <span className="brand-title">ILM AI</span>
              <p className="brand-subtitle">Assistant coranique fiable</p>
            </div>
          </Link>
        </div>

        <div className="top-bar-right">
          <div className="user-pill">
            {displayAvatarUrl ? (
              <img src={displayAvatarUrl} alt={displayName} className="user-pill-avatar" />
            ) : (
              <span className="user-pill-initials">{displayInitials}</span>
            )}
            <div>
              <strong>{displayName}</strong>
              <small>Connecté</small>
            </div>
          </div>

          <div className="session-actions">
            <Show when="signed-in">
              <SignOutButton>
                <button className="auth-ghost-button header-auth-button" type="button">
                  Se déconnecter
                </button>
              </SignOutButton>
            </Show>
            <Show when="signed-out">
              <SignInButton mode="modal">
                <button className="auth-solid-button header-auth-button" type="button">
                  Se connecter
                </button>
              </SignInButton>
            </Show>
          </div>
        </div>
      </header>

      {/* Overlay pour fermer la sidebar sur mobile en cliquant a l'exterieur */}
      {isSidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)}></div>
      )}

      <main className="chat-main-container">
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

          {/* Carte Historique */}
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
                  <h2>Votre nouvelle discussion</h2>
                  <p>Posez votre question et profitez d'une assistance ciblée, conservée même après rafraîchissement.</p>
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

                return (
                  <div key={message.id} className="assistant-stack message-enter">
                    {message.error_id ? (
                      <div className="error-message-row">
                        <div className="error-bubble">
                          <div className="error-header">
                            <span className="material-symbols-outlined">report</span>
                            <span>Perturbation technique</span>
                          </div>
                          <p className="error-text">{message.displayedAnswer || message.answer}</p>
                          <div className="error-footer">
                            <span>Identifiant :</span>
                            <span 
                              className="error-id-tag" 
                              onClick={() => {
                                navigator.clipboard.writeText(message.error_id);
                                alert("ID de l'erreur copié !");
                              }}
                              title="Copier l'ID"
                            >
                              {message.error_id}
                            </span>
                          </div>
                        </div>
                      </div>
                    ) : (
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
                    )}

                    {!message.isComplete && (
                      <div className="typing-indicator" aria-label="Assistant en train d'écrire">
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
      </main>

      <div className="composer-shell">
        <p className="composer-disclaimer">
          Avertissement : Ce service ne constitue pas une fatwa. Vérifiez les réponses de l’IA avec des sources authentiques.
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
            aria-label={isGenerating ? 'Interrompre la réponse' : 'Envoyer'}
            onClick={isGenerating ? stopGeneration : undefined}
            disabled={!isGenerating && !questionInput.trim()}
          >
            <span className="material-symbols-outlined send-icon">
              {isGenerating ? 'stop' : 'arrow_upward'}
            </span>
          </button>
        </form>
      </div>
    </div>
  );
}
