"use client";

import { useState } from "react";
import type { BloodGroup, BloodBank } from "@/lib/types";
import { BLOOD_GROUPS, BLOOD_GROUP_COLORS } from "@/lib/types";

const mockBloodBanks: BloodBank[] = [
  {
    bank_id: "bb001", name: "Apollo Blood Bank", district: "Hyderabad", state: "Telangana",
    contact_phone: "+91 40-2345-6789",
    inventory: {
      "O+": { units_available: 5, expiry_date: "2026-10-15", reserved_count: 1 },
      "A+": { units_available: 3, expiry_date: "2026-09-28", reserved_count: 0 },
      "B+": { units_available: 2, expiry_date: "2026-06-12", reserved_count: 0 },
    },
  },
  {
    bank_id: "bb002", name: "NIMS Blood Centre", district: "Hyderabad", state: "Telangana",
    contact_phone: "+91 40-2348-9012",
    inventory: {
      "B+": { units_available: 4, expiry_date: "2026-09-20", reserved_count: 0 },
      "O-": { units_available: 1, expiry_date: "2026-07-15", reserved_count: 0 },
      "A+": { units_available: 2, expiry_date: "2026-08-30", reserved_count: 1 },
    },
  },
  {
    bank_id: "bb003", name: "Indian Red Cross Blood Bank", district: "Secunderabad", state: "Telangana",
    contact_phone: "+91 40-2789-0123",
    inventory: {
      "AB+": { units_available: 2, expiry_date: "2026-10-02", reserved_count: 0 },
      "O+": { units_available: 3, expiry_date: "2026-09-15", reserved_count: 0 },
    },
  },
  {
    bank_id: "bb004", name: "Yashoda Blood Bank", district: "Hyderabad", state: "Telangana",
    contact_phone: "+91 40-4567-8901",
    inventory: {
      "A+": { units_available: 6, expiry_date: "2026-10-20", reserved_count: 2 },
      "O+": { units_available: 4, expiry_date: "2026-09-10", reserved_count: 0 },
      "B-": { units_available: 1, expiry_date: "2026-06-09", reserved_count: 0 },
    },
  },
  {
    bank_id: "bb005", name: "KIMS Blood Centre", district: "Warangal", state: "Telangana",
    contact_phone: "+91 870-234-5678",
    inventory: {
      "O+": { units_available: 2, expiry_date: "2026-08-25", reserved_count: 0 },
      "B+": { units_available: 3, expiry_date: "2026-09-05", reserved_count: 0 },
      "A-": { units_available: 1, expiry_date: "2026-07-20", reserved_count: 0 },
    },
  },
  {
    bank_id: "bb006", name: "Care Hospital Blood Bank", district: "Hyderabad", state: "Telangana",
    contact_phone: "+91 40-3456-7890",
    inventory: {
      "O+": { units_available: 7, expiry_date: "2026-11-01", reserved_count: 0 },
      "O-": { units_available: 2, expiry_date: "2026-08-15", reserved_count: 1 },
      "AB+": { units_available: 3, expiry_date: "2026-09-30", reserved_count: 0 },
    },
  },
  {
    bank_id: "bb007", name: "Continental Blood Centre", district: "Hyderabad", state: "Telangana",
    contact_phone: "+91 40-6789-0123",
    inventory: {
      "B+": { units_available: 5, expiry_date: "2026-10-10", reserved_count: 0 },
      "A+": { units_available: 4, expiry_date: "2026-09-22", reserved_count: 0 },
      "AB-": { units_available: 1, expiry_date: "2026-07-05", reserved_count: 0 },
    },
  },
  {
    bank_id: "bb008", name: "Rainbow Children Blood Bank", district: "Hyderabad", state: "Telangana",
    contact_phone: "+91 40-2345-0000",
    inventory: {
      "O+": { units_available: 3, expiry_date: "2026-08-18", reserved_count: 0 },
      "A+": { units_available: 2, expiry_date: "2026-09-12", reserved_count: 0 },
      "B+": { units_available: 1, expiry_date: "2026-06-15", reserved_count: 0 },
    },
  },
];

function getDaysUntilExpiry(dateStr: string) {
  const now = new Date("2026-06-06");
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
  const [banks, setBanks] = useState(mockBloodBanks);
  const [searchGroup, setSearchGroup] = useState<string>("");
  const [searchDistrict, setSearchDistrict] = useState("");
  const [reserved, setReserved] = useState<Set<string>>(new Set());

  const totals = getTotalsByGroup(banks);

  const filteredBanks = banks.filter((bank) => {
    if (searchDistrict && !bank.district.toLowerCase().includes(searchDistrict.toLowerCase())) return false;
    if (searchGroup && !(bank.inventory[searchGroup]?.units_available > 0)) return false;
    return true;
  });

  const handleReserve = (bankId: string, group: string) => {
    const key = `${bankId}-${group}`;
    if (reserved.has(key)) return;
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
  };

  const expiringStock = banks.flatMap((bank) =>
    Object.entries(bank.inventory)
      .filter(([, data]) => getDaysUntilExpiry(data.expiry_date) <= 7 && data.units_available > 0)
      .map(([group, data]) => ({
        bank: bank.name,
        district: bank.district,
        group,
        units: data.units_available,
        daysLeft: getDaysUntilExpiry(data.expiry_date),
      }))
  );

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold">Blood Bank Inventory</h1>
      <p className="mb-8 text-[var(--text-secondary)]">
        Real-time stock across partner blood banks. Search, reserve, and track expiry.
      </p>

      {/* Totals by Blood Group */}
      <div className="mb-8 grid grid-cols-4 gap-3 sm:grid-cols-8">
        {BLOOD_GROUPS.map((group) => (
          <button
            key={group}
            onClick={() => setSearchGroup(searchGroup === group ? "" : group)}
            className={`rounded-xl border p-4 text-center transition-all ${
              searchGroup === group
                ? "border-[var(--blood)] bg-[var(--blood)]/10"
                : "border-border bg-card hover:bg-card-hover"
            }`}
          >
            <span
              className="text-lg font-bold"
              style={{ color: BLOOD_GROUP_COLORS[group] }}
            >
              {group}
            </span>
            <p className="mt-1 text-2xl font-bold">{totals[group] || 0}</p>
            <p className="text-xs text-[var(--text-muted)]">units</p>
          </button>
        ))}
      </div>

      {/* Expiry Alerts */}
      {expiringStock.length > 0 && (
        <div className="mb-6 rounded-xl border border-[var(--orange)]/30 bg-[var(--orange)]/5 p-4">
          <p className="mb-2 text-sm font-semibold text-[var(--orange)]">
            Expiry Alerts ({expiringStock.length} items expiring within 7 days)
          </p>
          <div className="flex flex-wrap gap-2">
            {expiringStock.map((item, i) => (
              <span
                key={i}
                className="rounded-lg bg-[var(--orange)]/15 px-3 py-1 text-xs text-[var(--orange)]"
              >
                {item.bank} — {item.group}: {item.units} units ({item.daysLeft}d left)
              </span>
            ))}
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
          className="rounded-xl border border-border bg-surface px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-info focus:outline-none"
        />
        {searchGroup && (
          <button
            onClick={() => setSearchGroup("")}
            className="rounded-xl border border-border bg-card px-4 py-3 text-sm text-[var(--text-secondary)] hover:bg-card-hover"
          >
            Clear filter: {searchGroup}
          </button>
        )}
      </div>

      {/* Bank Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredBanks.map((bank) => (
          <div
            key={bank.bank_id}
            className="rounded-2xl border border-border bg-card p-6 transition-all hover:bg-card-hover"
          >
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold">{bank.name}</h3>
                <p className="text-sm text-[var(--text-muted)]">
                  {bank.district}, {bank.state}
                </p>
              </div>
              <p className="text-xs text-[var(--text-muted)]">{bank.contact_phone}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              {Object.entries(bank.inventory).map(([group, data]) => {
                const daysLeft = getDaysUntilExpiry(data.expiry_date);
                const isReserved = reserved.has(`${bank.bank_id}-${group}`);
                return (
                  <div
                    key={group}
                    className="flex-1 rounded-xl border border-border bg-surface p-3"
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className="text-sm font-bold"
                        style={{ color: BLOOD_GROUP_COLORS[group as BloodGroup] }}
                      >
                        {group}
                      </span>
                      {daysLeft <= 7 && (
                        <span className="rounded bg-[var(--orange)]/20 px-1.5 py-0.5 text-[10px] text-[var(--orange)]">
                          {daysLeft}d
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-2xl font-bold">{data.units_available}</p>
                    <p className="text-xs text-[var(--text-muted)]">
                      {data.reserved_count > 0 && `${data.reserved_count} reserved · `}
                      expires {data.expiry_date}
                    </p>
                    {data.units_available > 0 && (
                      <button
                        onClick={() => handleReserve(bank.bank_id, group)}
                        disabled={isReserved}
                        className={`mt-2 w-full rounded-lg py-1.5 text-xs font-semibold transition-all ${
                          isReserved
                            ? "bg-success/20 text-success"
                            : "bg-blood/20 text-blood hover:bg-blood/30"
                        }`}
                      >
                        {isReserved ? "Reserved" : "Reserve 1 Unit"}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {filteredBanks.length === 0 && (
        <div className="mt-12 rounded-2xl border border-border bg-card p-12 text-center">
          <p className="text-lg font-semibold text-[var(--text-secondary)]">
            No blood banks found with {searchGroup || "available stock"}
          </p>
          <p className="mt-2 text-sm text-[var(--text-muted)]">
            Activating donor search...
          </p>
          <a
            href="/donor-outreach"
            className="mt-4 inline-block rounded-xl bg-blood px-6 py-3 text-sm font-semibold text-white"
          >
            Start Voice Call Campaign &rarr;
          </a>
        </div>
      )}
    </div>
  );
}
