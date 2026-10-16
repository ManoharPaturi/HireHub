import React, { useEffect, useState, useRef, useCallback } from 'react';
import { messageService } from '../../services/api';
import { ChatMessage, MessageContact } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { Send, MessageSquare, ArrowLeft } from 'lucide-react';

const FALLBACK_AVATAR = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=120&q=80';

export const MessagesView: React.FC<{ initialUserId?: number | null }> = ({ initialUserId }) => {
  const { user } = useAuth();
  const isRecruiter = user?.role === 'recruiter';

  const [contacts, setContacts] = useState<MessageContact[]>([]);
  const [selected, setSelected] = useState<MessageContact | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingThread, setLoadingThread] = useState(false);
  const [error, setError] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  const fetchContacts = useCallback(async () => {
    try {
      const list = await messageService.getContacts();
      setContacts(list);
      return list;
    } catch (e) { console.error(e); return []; }
    finally { setLoading(false); }
  }, []);

  const openThread = useCallback(async (contact: MessageContact) => {
    setSelected(contact);
    setLoadingThread(true);
    setError('');
    try {
      setMessages(await messageService.getMessages(contact.user_id));
      fetchContacts(); // refresh unread counts
    } catch (e) { console.error(e); }
    finally { setLoadingThread(false); }
  }, [fetchContacts]);

  // Keep the open thread fresh so replies from the other side appear live.
  useEffect(() => {
    if (!selected) return;
    const t = setInterval(async () => {
      try {
        const fresh = await messageService.getMessages(selected.user_id);
        setMessages((prev) => (fresh.length !== prev.length ? fresh : prev));
      } catch { /* ignore */ }
    }, 10000);
    return () => clearInterval(t);
  }, [selected]);

  useEffect(() => {
    (async () => {
      const list = await fetchContacts();
      // Deep link (e.g. "Message" on an applicant card): open that thread.
      if (initialUserId && list.some((c) => c.user_id === initialUserId)) {
        openThread(list.find((c) => c.user_id === initialUserId)!);
      }
    })();
    // Light polling so new incoming messages / unread badges stay fresh.
    const t = setInterval(fetchContacts, 15000);
    return () => clearInterval(t);
  }, [fetchContacts, openThread, initialUserId]);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loadingThread]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMsg.trim() || !selected || sending) return;
    setSending(true);
    setError('');
    try {
      const sent = await messageService.sendMessage(selected.user_id, newMsg);
      setMessages((prev) => [...prev, sent]);
      setNewMsg('');
      fetchContacts();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to send. Please try again.');
    } finally { setSending(false); }
  };

  const fmtTime = (iso: string) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className={isRecruiter ? 'max-w-6xl mx-auto' : 'max-w-6xl mx-auto px-4 sm:px-6 py-8'}>
      <div className="card overflow-hidden flex" style={{ height: 'calc(100vh - 220px)', minHeight: '480px' }}>
        {/* Contacts list */}
        <aside
          className={`${selected ? 'hidden md:flex' : 'flex'} flex-col w-full md:w-72 lg:w-80 flex-shrink-0`}
          style={{ borderRight: '1px solid var(--border)' }}
        >
          <div className="px-4 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
            <h2 className="font-extrabold text-base flex items-center gap-2">
              <MessageSquare className="w-4 h-4" style={{ color: 'var(--primary)' }} /> Messages
            </h2>
            <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>
              {isRecruiter ? 'Candidates who applied to your roles' : 'Recruiters from your applications'}
            </p>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {loading ? (
              [1, 2, 3].map((n) => <div key={n} className="p-3 rounded-xl mb-1"><div className="flex items-center gap-3"><div className="w-10 h-10 rounded-xl skeleton" /><div className="flex-1 space-y-2"><div className="h-2.5 w-2/3 skeleton" /><div className="h-2 w-full skeleton" /></div></div></div>)
            ) : contacts.length === 0 ? (
              <div className="text-center py-10 px-4">
                <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}>
                  <MessageSquare className="w-6 h-6" style={{ color: 'var(--muted-2)' }} />
                </div>
                <p className="text-sm font-semibold">No conversations yet</p>
                <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>
                  {isRecruiter ? 'When students apply to your internships, they appear here.' : 'Apply to internships to connect with recruiters here.'}
                </p>
              </div>
            ) : (
              contacts.map((c) => {
                const active = selected?.user_id === c.user_id;
                return (
                  <button
                    key={c.user_id}
                    onClick={() => openThread(c)}
                    className="w-full text-left p-3 rounded-xl flex items-center gap-3 transition mb-1"
                    style={active ? { background: 'var(--primary-soft)' } : undefined}
                    onMouseEnter={(e) => { if (!active) e.currentTarget.style.background = 'var(--surface-2)'; }}
                    onMouseLeave={(e) => { if (!active) e.currentTarget.style.background = 'transparent'; }}
                  >
                    <img src={c.avatar_url || FALLBACK_AVATAR} alt="" className="w-10 h-10 rounded-xl object-cover flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-sm font-bold truncate">{c.full_name}</p>
                        {c.unread ? <span className="text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center text-white flex-shrink-0" style={{ background: 'var(--primary)' }}>{c.unread}</span> : null}
                      </div>
                      <p className="text-[11px] truncate" style={{ color: 'var(--muted)' }}>{c.subtitle}</p>
                      <p className="text-[11px] truncate mt-0.5" style={{ color: 'var(--muted-2)' }}>{c.last_message || `Re: ${c.internship_title}`}</p>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </aside>

        {/* Thread */}
        <section className={`${selected ? 'flex' : 'hidden md:flex'} flex-col flex-1 min-w-0`}>
          {selected ? (
            <>
              <div className="px-4 py-3 flex items-center gap-3" style={{ borderBottom: '1px solid var(--border)' }}>
                <button className="md:hidden w-8 h-8 rounded-lg flex items-center justify-center" style={{ color: 'var(--muted)' }} onClick={() => setSelected(null)}>
                  <ArrowLeft className="w-4 h-4" />
                </button>
                <img src={selected.avatar_url || FALLBACK_AVATAR} alt="" className="w-9 h-9 rounded-xl object-cover" />
                <div className="min-w-0">
                  <p className="text-sm font-bold truncate">{selected.full_name}</p>
                  <p className="text-[11px] truncate" style={{ color: 'var(--muted)' }}>{selected.subtitle}</p>
                </div>
              </div>

              <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
                {loadingThread ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((n) => <div key={n} className="h-12 rounded-xl skeleton" style={{ maxWidth: `${70 - n * 10}%` }} />)}
                  </div>
                ) : messages.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-center px-6">
                    <div>
                      <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}>
                        <MessageSquare className="w-6 h-6" style={{ color: 'var(--muted-2)' }} />
                      </div>
                      <p className="text-sm font-semibold">Start the conversation</p>
                      <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>
                        Say hello regarding <strong>{selected.internship_title}</strong>.
                      </p>
                    </div>
                  </div>
                ) : (
                  messages.map((m) => {
                    const mine = m.sender_id === user?.id;
                    return (
                      <div key={m.id} className={`flex ${mine ? 'justify-end' : 'justify-start'}`}>
                        <div
                          className="max-w-[78%] px-3.5 py-2.5 rounded-2xl"
                          style={mine
                            ? { background: 'var(--primary)', color: 'white', borderBottomRightRadius: '6px' }
                            : { background: 'var(--surface-2)', color: 'var(--text)', borderBottomLeftRadius: '6px', border: '1px solid var(--border)' }}
                        >
                          <p className="text-sm leading-snug whitespace-pre-wrap break-words">{m.content}</p>
                          <p className="text-[10px] mt-1 text-right opacity-70">{fmtTime(m.sent_at)}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {error && (
                <div className="px-4 py-2 text-xs font-semibold" style={{ color: 'var(--danger)' }}>{error}</div>
              )}

              <form onSubmit={handleSend} className="p-3 flex items-center gap-2" style={{ borderTop: '1px solid var(--border)' }}>
                <input
                  value={newMsg}
                  onChange={(e) => setNewMsg(e.target.value)}
                  placeholder="Write a message…"
                  className="input flex-1"
                />
                <button type="submit" disabled={!newMsg.trim() || sending} className="btn btn-primary !px-3.5 disabled:opacity-40">
                  {sending ? '…' : <Send className="w-4 h-4" />}
                </button>
              </form>
            </>
          ) : (
            <div className="h-full flex items-center justify-center text-center px-6">
              <div>
                <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}>
                  <MessageSquare className="w-7 h-7" style={{ color: 'var(--muted-2)' }} />
                </div>
                <p className="text-sm font-semibold">Select a conversation</p>
                <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Choose someone from the list to start chatting.</p>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};
