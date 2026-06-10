"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import type { BloodGroup, BloodBank } from "@/lib/types";
import { BLOOD_GROUPS, BLOOD_GROUP_COLORS } from "@/lib/types";
import { Badge } from "@/components/Badge";
import { Card } from "@/components/Card";
import { Warning } from "@phosphor-icons/react";
import { api } from "@/lib/api";

function getDaysUntilExpiry(dateStr: string) {
  const now = new Date();
  const expiry = new Date(dateStr);
  return Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function getTotalsByGroup(banks: BloodBank[]) {
  const totals: Record<string, number> = {};
  banks.forEach((bank) => {
    Object.entries(bank.inventory).forEach(([group, data]) => {
      totals[group] = (totals[group] || 0) + data.units_available;
    });
  });
  return totals;
}

export default function BloodBankPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--blood-pink)]"></div>
      </div>
    }>
      <BloodBankContent />
    </Suspense>
  );
}

function BloodBankContent() {
  const searchParams = useSearchParams();
  const urlBloodGroup = searchParams.get("blood_group") || "";

  const [banks, setBanks] = useState<BloodBank[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchGroup, setSearchGroup] = useState<string>(urlBloodGroup);
  const [searchDistrict, setSearchDistrict] = useState("");
  const [reserved, setReserved] = useState<Set<string>>(new Set());
  const [expiryAlerts, setExpiryAlerts] = useState<Array<{bank: string; district: string; group: string; units: number; daysLeft: number}>>([]);

  const totals = getTotalsByGroup(banks);

  useEffect(() => {
    fetchBanks();
    fetchExpiryAlerts();
  }, []);

  async function fetchBanks() {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get<BloodBank[]>("/api/blood-bank");
      setBanks(data);
    } catch (err) {
      setError("Failed to load blood bank inventory. Check backend connection.");
      console.error("Failed to fetch blood banks:", err);
    } finally {
      setLoading(false);
    }
  }

  async function fetchExpiryAlerts() {
    try {
      const alerts = await api.get<Array<{bank: string; district: string; group: string; units: number; daysLeft: number}>>("/api/blood-bank/expiry?days=7");
      setExpiryAlerts(alerts);
    } catch (err) {
      console.error("Failed to fetch expiry alerts:", err);
    }
  }

  async function handleSearch() {
    if (!searchGroup && !searchDistrict) {
      fetchBanks();
      return;
    }
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchGroup) params.append("blood_group", searchGroup);
      if (searchDistrict) params.append("district", searchDistrict);
      const data = await api.get<BloodBank[]>(`/api/blood-bank/search?${params}`);
      setBanks(data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleReserve(bankId: string, group: string) {
    const key = `${bankId}-${group}`;
    if (reserved.has(key)) return;

    try {
      await api.post("/api/blood-bank/reserve", {
        bank_id: bankId,
        blood_group: group,
        units: 1,
      });
      setReserved((prev) => new Set(prev).add(key));
      setBanks((prev) =>
        prev.map((bank) => {
          if (bank.bank_id !== bankId) return bank;
          const inv = bank.inventory[group];
          if (!inv || inv.units_available <= 0) return bank;
          return {
            ...bank,
            inventory: {
              ...bank.inventory,
              [group]: { ...inv, units_available: inv.units_available - 1, reserved_count: inv.reserved_count + 1 },
            },
          };
        })
      );
    } catch (err) {
      console.error("Reserve failed:", err);
      alert("Failed to reserve unit. Please try again.");
    }
  }

  const filteredBanks = banks.filter((bank) => {
    if (searchDistrict && !bank.district.toLowerCase().includes(searchDistrict.toLowerCase())) return false;
    if (searchGroup && !(bank.inventory[searchGroup]?.units_available > 0)) return false;
    return true;
  });

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold font-display">Blood Bank Inventory</h1>
      <p className="mb-8 text-secondary">
        Real-time stock across partner blood banks. Search, reserve, and track expiry.
      </p>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--blood-pink)] mx-auto mb-4"></div>
            <p className="text-secondary">Loading inventory...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="rounded-xl border border-warning/30 bg-warning/5 p-8 text-center">
          <Warning size={48} weight="regular" className="mx-auto mb-4" style={{ color: "var(--warning)" }} />
          <p className="text-lg font-semibold text-warning mb-2">{error}</p>
          <button
            onClick={fetchBanks}
            className="mt-4 rounded-lg bg-blood px-6 py-3 text-sm font-semibold text-white hover:brightness-110 transition-all"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Content */}
      {!loading && !error && (
        <>
      {/* Totals by Blood Group */}
      <div className="mb-8 grid grid-cols-4 gap-3 sm:grid-cols-8">
        {BLOOD_GROUPS.map((group) => (
          <button
            key={group}
            onClick={() => setSearchGroup(searchGroup === group ? "" : group)}
            className={`rounded-xl border p-4 text-center transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] ${
              searchGroup === group
                ? "border-blood bg-blood/10"
                : "border-border bg-card hover:bg-card-hover"
            }`}
          >
            <span
              className="text-lg font-bold font-mono"
              style={{ color: BLOOD_GROUP_COLORS[group] }}
            >
              {group}
            </span>
            <p className="mt-1 text-2xl font-bold font-display">{totals[group] || 0}</p>
            <p className="text-xs text-muted">units</p>
          </button>
        ))}
      </div>

      {/* Expiry Alerts */}
      {expiryAlerts.length > 0 && (
        <div className="mb-6 flex items-start gap-3 rounded-xl border border-warning/30 bg-warning/5 p-4">
          <Warning className="mt-0.5 shrink-0" size={20} weight="regular" style={{ color: "var(--warning)" }} />
          <div>
            <p className="text-sm font-semibold font-display text-warning">
              Expiry Alerts ({expiryAlerts.length} items expiring within 7 days)
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {expiryAlerts.map((item, i) => (
                <span
                  key={i}
                  className="rounded-lg bg-warning/15 px-3 py-1 text-xs text-warning"
                >
                  {item.bank} — {item.group}: {item.units} units ({item.daysLeft}d left)
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="Search district..."
          value={searchDistrict}
          onChange={(e) => setSearchDistrict(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSearch()}
          className="rounded-lg border border-border bg-surface px-4 py-3 text-sm text-primary placeholder-muted focus:border-[var(--border-focus)] focus:ring-2 focus:ring-[var(--border-focus)]/20 focus:outline-none"
        />
        <button
          onClick={handleSearch}
          className="rounded-lg bg-blood px-6 py-3 text-sm font-semibold text-white hover:brightness-110 transition-colors"
        >
          Search
        </button>
        {searchGroup && (
          <button
            onClick={() => { setSearchGroup(""); fetchBanks(); }}
            className="rounded-lg border border-border bg-card px-4 py-3 text-sm text-secondary hover:bg-card-hover transition-colors"
          >
            Clear filter: {searchGroup}
          </button>
        )}
      </div>

      {/* Bank Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredBanks.map((bank) => (
          <Card key={bank.bank_id} hover>
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold font-display">{bank.name}</h3>
                <p className="text-sm text-muted">
                  {bank.district}, {bank.state}
                </p>
              </div>
              <p className="text-xs text-muted font-mono">{bank.contact_phone}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              {Object.entries(bank.inventory).map(([group, data]) => {
                const daysLeft = getDaysUntilExpiry(data.expiry_date);
                const isReserved = reserved.has(`${bank.bank_id}-${group}`);
                return (
                  <div
                    key={group}
                    className="flex-1 rounded-lg border border-border bg-surface p-3"
                  >
                    <div className="flex items-center justify-between">
                      <Badge type="blood" value={group as BloodGroup} />
                      {daysLeft <= 7 && (
                        <span className="rounded bg-warning/20 px-1.5 py-0.5 text-[10px] font-mono text-warning">
                          {daysLeft}d
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-2xl font-bold font-mono">{data.units_available}</p>
                    <p className="text-xs text-muted">
                      {data.reserved_count > 0 && `${data.reserved_count} reserved · `}
                      expires {data.expiry_date}
                    </p>
                    {data.units_available > 0 && (
                      <button
                        onClick={() => handleReserve(bank.bank_id, group)}
                        disabled={isReserved}
                        className={`mt-2 w-full rounded-lg py-1.5 text-xs font-semibold font-display transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                          isReserved
                            ? "bg-success/20 text-success cursor-default"
                            : "bg-blood/20 text-blood hover:bg-blood/30 active:scale-[0.98]"
                        }`}
                      >
                        {isReserved ? "Reserved" : "Reserve 1 Unit"}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </Card>
        ))}
      </div>

      {filteredBanks.length === 0 && (
        <Card className="mt-12 text-center">
          <p className="text-lg font-semibold font-display text-secondary">
            No blood banks found with {searchGroup || "available stock"}
          </p>
          <p className="mt-2 text-sm text-muted">
            Activating donor search...
          </p>
          <a
            href="/donor-outreach"
            className="mt-4 inline-block rounded-lg bg-blood px-6 py-3 text-sm font-semibold font-display text-white hover:brightness-110 active:scale-[0.98] transition-all"
          >
            Start Voice Call Campaign &rarr;
          </a>
        </Card>
      )}
        </>
      )}
    </div>
  );
}
