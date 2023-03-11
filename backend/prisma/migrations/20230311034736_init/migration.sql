-- CreateTable
CREATE TABLE "Player" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "name" TEXT NOT NULL,
    "firstName" TEXT,
    "middleName" TEXT,
    "lastName" TEXT,
    "useName" TEXT,
    "primaryPosition" TEXT,
    "primaryNumber" INTEGER,
    "birthStateProvince" TEXT,
    "birthCountry" TEXT,
    "birthCity" TEXT,
    "birthDate" TIMESTAMP(3),
    "height" INTEGER,
    "weight" INTEGER,
    "active" BOOLEAN,
    "currentTeamId" TEXT,
    "parentOrgId" TEXT,
    "draftYear" INTEGER,
    "mlbId" TEXT,
    "bbrefId" TEXT,
    "bbrefMinorsId" TEXT,
    "retroId" TEXT,
    "fangraphsId" TEXT,
    "fangraphsMinorMasterId" TEXT,
    "fangraphsOrgProspectRanking" INTEGER,
    "fangraphsOverallProspectRanking" INTEGER,

    CONSTRAINT "Player_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Player_mlbId_key" ON "Player"("mlbId");

-- CreateIndex
CREATE UNIQUE INDEX "Player_bbrefId_key" ON "Player"("bbrefId");

-- CreateIndex
CREATE UNIQUE INDEX "Player_bbrefMinorsId_key" ON "Player"("bbrefMinorsId");

-- CreateIndex
CREATE UNIQUE INDEX "Player_retroId_key" ON "Player"("retroId");
