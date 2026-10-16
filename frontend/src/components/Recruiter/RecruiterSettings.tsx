/*
 * Settings-screen layout. Toggle values currently live only in component
 * state and do not save through the API. Password, email and deactivation
 * buttons are presentation controls without implemented handlers here.
 */

import React from 'react';
import { Bell, Shield, AlertTriangle, Lock, Mail } from 'lucide-react';

export const RecruiterSettings: React.FC = () => {
  return (
    <div className="max-w-3xl space-y-5">
      {/* Notifications */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}><Bell className="w-4 h-4" /></div>
          <h3 className="font-bold text-base">Notifications</h3>
        </div>
        <p className="text-xs mb-4" style={{ color: 'var(--muted)' }}>Control when and how we contact you.</p>
        <div className="space-y-1">
          <Toggle label="Email notifications" desc="Receive alerts when someone applies" defaultChecked />
          <Toggle label="Interview reminders" desc="Get notified 30 minutes before interviews" defaultChecked />
          <Toggle label="Weekly digest" desc="A summary of your pipeline every Monday" />
        </div>
      </div>

      {/* Security */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'var(--success-soft)', color: 'var(--success)' }}><Shield className="w-4 h-4" /></div>
          <h3 className="font-bold text-base">Security</h3>
        </div>
        <p className="text-xs mb-4" style={{ color: 'var(--muted)' }}>Keep your account secure.</p>
        <div className="space-y-2">
          <button className="btn btn-ghost text-xs w-full justify-start"><Lock className="w-4 h-4" /> Change password</button>
          <button className="btn btn-ghost text-xs w-full justify-start"><Mail className="w-4 h-4" /> Manage email</button>
        </div>
      </div>

      {/* Danger zone */}
      <div className="card p-6" style={{ borderColor: 'color-mix(in srgb, var(--danger) 25%, var(--border))', background: 'color-mix(in srgb, var(--danger) 3%, var(--surface))' }}>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'var(--danger-soft)', color: 'var(--danger)' }}><AlertTriangle className="w-4 h-4" /></div>
          <h3 className="font-bold text-base" style={{ color: 'var(--danger)' }}>Danger zone</h3>
        </div>
        <p className="text-xs mb-4" style={{ color: 'var(--muted)' }}>Once you delete your account, there is no going back. Please be certain.</p>
        <button className="btn btn-danger-soft text-xs">Deactivate account</button>
      </div>
    </div>
  );
};

// This switch updates only local state. Reloading/remounting resets it
// to defaultChecked because no preference API is connected.
const Toggle: React.FC<{ label: string; desc: string; defaultChecked?: boolean }> = ({ label, desc, defaultChecked }) => {
  const [on, setOn] = React.useState(!!defaultChecked);
  return (
    <div className="flex items-center justify-between py-3" style={{ borderBottom: '1px solid var(--border)' }}>
      <div>
        <p className="text-sm font-semibold">{label}</p>
        <p className="text-xs" style={{ color: 'var(--muted)' }}>{desc}</p>
      </div>
      <button
        type="button"
        onClick={() => setOn(!on)}
        className="relative w-11 h-6 rounded-full transition flex-shrink-0"
        style={{ background: on ? 'var(--primary)' : 'var(--surface-3)' }}
        aria-pressed={on}
      >
        <span className="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform" style={{ transform: on ? 'translateX(20px)' : 'translateX(0)' }} />
      </button>
    </div>
  );
};
