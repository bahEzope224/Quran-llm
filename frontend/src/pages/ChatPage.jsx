import {
  Show,
  SignInButton,
  SignOutButton,
  SignUpButton,
  useUser,
} from '@clerk/react';
import { useEffect, useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8000';
const defaultQuestion = 'Quelles sont les vertus de la patience selon le Coran et les Hadiths ?';

const legalSchools = ['Hanafi', 'Maliki', 'Shafi‘i', 'Hanbali'];
const languages = ['Francais', 'Arabe', 'Anglais'];
const modes = ['Clair', 'Approfondi', 'Concise'];

const fallbackResponse = {
  answer:
    "La patience est une vertu centrale en Islam. Elle apparait dans le Coran comme une preuve de sincerite dans l'epreuve, elle est expliquee par les savants comme une perseverance active, et les hadiths montrent qu'elle transforme les difficultes en bien pour le croyant.",
  sources: [
    {
      type: 'quran',
      ref: '29:2',
      text: "Les gens pensent-ils qu'on les laissera dire : Nous croyons, sans les eprouver ?",
      source: 'Coran',
      arabic: 'أَحَسِبَ النَّاسُ أَنْ يُتْرَكُوا أَنْ يَقُولُوا آمَنَّا وَهُمْ لَا يُفْتَنُونَ',
      role: "Texte source principal sur l'epreuve et la sincerite de la foi.",
    },
    {
      type: 'tafsir',
      ref: 'Ibn Kathir 29:2',
      text:
        "L'epreuve distingue la veracite de la foi et appelle a une patience active dans la perseverance.",
      source: 'Tafsir Ibn Kathir',
      role: 'Explication savante du verset et de sa portee.',
    },
    {
      type: 'hadith',
      ref: 'Muslim 2999',
      text:
        "L'etonnant est le cas du croyant. Tout ce qui lui arrive est un bien. S'il est touche par un malheur, il patiente et c'est un bien pour lui.",
      source: 'Sahih Muslim',
      role: 'Confirmation prophetique de la valeur spirituelle de la patience.',
    },
  ],
};

const fallbackProfile = {
  name: 'Ibrahima Bah',
  avatar_initials: 'IB',
  legal_school: 'Maliki',
  language: 'Francais',
  mode: 'Clair',
  notifications_enabled: true,
};

function toSourceCard(source, index) {
  const fallbackSourceName =
    source.type === 'quran'
      ? 'Coran'
      : source.type === 'tafsir'
        ? 'Tafsir'
        : 'Hadith';

  return {
    id: `${source.type}-${index}`,
    icon:
      source.type === 'quran'
        ? 'auto_stories'
        : source.type === 'tafsir'
          ? 'menu_book'
          : 'history_edu',
    source: source.source ?? fallbackSourceName,
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

export default function ChatPage() {
  const { isLoaded: isUserLoaded, user } = useUser();
  const [activeView, setActiveView] = useState('response');
  const [activeScreen, setActiveScreen] = useState('chat');
  const [questionInput, setQuestionInput] = useState(defaultQuestion);
  const [chatData, setChatData] = useState(fallbackResponse);
  const [lastQuestion, setLastQuestion] = useState(defaultQuestion);
  const [profile, setProfile] = useState(fallbackProfile);
  const [isLoadingChat, setIsLoadingChat] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [chatError, setChatError] = useState('');
  const [profileError, setProfileError] = useState('');

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

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedQuestion = questionInput.trim();
    if (!trimmedQuestion) {
      return;
    }

    setIsLoadingChat(true);
    setChatError('');

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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
      setChatData(data);
      setLastQuestion(trimmedQuestion);
      setActiveView('response');
    } catch {
      setChatError('Le backend ne repond pas pour le moment. Affichage du contenu local.');
      setChatData(fallbackResponse);
      setLastQuestion(trimmedQuestion);
    } finally {
      setIsLoadingChat(false);
    }
  }

  const sourceCards = chatData.sources.map(toSourceCard);
  const evidenceHighlights = buildEvidenceHighlights(chatData.sources);
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
        <div className="brand-row">
          <span className="brand-title">ILM AI</span>
        </div>

        <div className="top-bar-actions">
          <div className="page-actions">
            {activeScreen === 'chat' ? (
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
            ) : (
              <span className="profile-header-label">Mon profil</span>
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
          </div>

          <div className="session-actions">
            <Show when="signed-out">
              <SignInButton mode="modal">
                <button className="auth-ghost-button header-auth-button" type="button">
                  Connexion
                </button>
              </SignInButton>

              <SignUpButton mode="modal">
                <button className="auth-solid-button header-auth-button" type="button">
                  Inscription
                </button>
              </SignUpButton>
            </Show>
          </div>
        </div>
      </header>

      <main className="chat-content">
        {activeScreen === 'chat' ? (
          <section className="chat-thread" aria-label="Historique de conversation">
            <div className="user-message-row">
              <article className="user-message">
                <p>{lastQuestion}</p>
              </article>
            </div>

            <div className="assistant-stack">
              {chatError ? <p className="status-banner warning">{chatError}</p> : null}

              {activeView === 'response' ? (
                <>
                  <article className="assistant-response-card">
                    <div className="assistant-card-header">
                      <div className="reliable-badge">
                        <span className="material-symbols-outlined fill">verified</span>
                        <span>Fiable</span>
                      </div>

                      <button className="copy-button" type="button">
                        <span className="material-symbols-outlined">content_copy</span>
                        <span>Copier</span>
                      </button>
                    </div>

                    <p className="assistant-response-text">{chatData.answer}</p>

                    <div className="tag-list" aria-label="Etiquettes">
                      {chatData.sources.map((source) => (
                        <span key={`${source.type}-${source.ref}`} className="topic-tag">
                          {source.type}
                        </span>
                      ))}
                    </div>
                  </article>

                  <div className="source-stack">
                    {sourceCards.map((card) => (
                      <SourceCard key={card.id} card={card} />
                    ))}
                  </div>
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
                        <span>{chatData.sources.length} sources</span>
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
                            <p className={`proof-excerpt ${card.type === 'hadith' ? 'italic' : ''}`}>
                              "{card.content}"
                            </p>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              )}

              <div className="feedback-row" aria-label="Evaluation de la reponse">
                <button className="feedback-button" type="button">
                  <span className="material-symbols-outlined">thumb_up</span>
                  <span>Utile</span>
                </button>
                <button className="feedback-button negative" type="button">
                  <span className="material-symbols-outlined">thumb_down</span>
                  <span>Imprecis</span>
                </button>
              </div>
            </div>

            {isLoadingChat ? (
              <div className="typing-indicator" aria-label="Assistant en train d'ecrire">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            ) : null}
          </section>
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
                <button className="activity-item" type="button">
                  <div>
                    <strong>Historique</strong>
                    <p>Retrouver les dernieres questions et reponses consultees.</p>
                  </div>
                  <span className="material-symbols-outlined">chevron_right</span>
                </button>

                <button className="activity-item" type="button">
                  <div>
                    <strong>Favoris</strong>
                    <p>Conserver les rappels, preuves et reponses utiles.</p>
                  </div>
                  <span className="material-symbols-outlined">chevron_right</span>
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
              disabled={isLoadingChat}
            />

            <button className="send-button" type="submit" aria-label="Envoyer" disabled={isLoadingChat}>
              <span className="material-symbols-outlined send-icon">
                {isLoadingChat ? 'hourglass_top' : 'arrow_upward'}
              </span>
            </button>
          </form>
        </div>
      ) : null}
    </div>
  );
}
